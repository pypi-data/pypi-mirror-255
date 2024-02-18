from django.db import models
from rest import settings

from rest import models as rm
from rest import helpers as rh
from taskqueue.models import Task
from account.models import Member
from objict import objict
from datetime import datetime, timedelta
from rest import log
from ws4redis import client as ws4redis
import time

logger = log.getLogger("incident", filename="incident.log")

EVENT_META_TO_INCIDENT = [
    "username",
    "email",
    "phone",
    "group_name",
    "group_id",
    "http_user_agent",
    "path"
]

INCIDENT_STATE_NEW = 0
INCIDENT_STATE_OPENED = 1
INCIDENT_STATE_PAUSED = 2
INCIDENT_STATE_IGNORE = 3
INCIDENT_STATE_RESOLVED = 4
INCIDENT_STATE_PENDING = 5

INCIDENT_STATES = [
    (INCIDENT_STATE_NEW, "new"),
    (INCIDENT_STATE_OPENED, "opened"),
    (INCIDENT_STATE_PAUSED, "paused"),
    (INCIDENT_STATE_IGNORE, "ignored"),
    (INCIDENT_STATE_RESOLVED, "resolved"),
    (INCIDENT_STATE_PENDING, "pending"),
]

INCIDENT_EMAIL_FROM = settings.get("INCIDENT_EMAIL_FROM", None)
if INCIDENT_EMAIL_FROM is None:
    INCIDENT_EMAIL_FROM = f"{settings.SITE_LABEL} INCIDENT <incident@{settings.EMAIL_DEFAULT_DOMAIN}>"


class Incident(models.Model, rm.RestModel, rm.MetaDataModel):
    class RestMeta:
        POST_SAVE_FIELDS = ["level", "catagory", "action"]
        SEARCH_FIELDS = ["description", "hostname"]
        VIEW_PERMS = ["view_incidents", "view_issues"]
        LIST_PARENT_KINDS = ["org", "iso"]
        LIST_CHILD_DEPTH = 3
        GRAPHS = {
            "default": {
                "extra": ["metadata", ("get_state_display", "state_display")],
                "graphs": {
                    "group": "basic",
                    "rule": "basic",
                    "assigned_to": "basic"
                },
            }
        }

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    description = models.CharField(max_length=200)

    category = models.CharField(max_length=124, null=True, default=None, db_index=True)

    component = models.CharField(max_length=200, null=True, default=None, db_index=True)
    component_id = models.IntegerField(null=True, blank=True, default=None, db_index=True)

    hostname = models.CharField(max_length=200, null=True, default=None, db_index=True)
    reporter_ip = models.CharField(max_length=16, blank=True, null=True, default=None, db_index=True)

    group = models.ForeignKey("account.Group", on_delete=models.SET_NULL, null=True, default=None)
    assigned_to = models.ForeignKey("account.Member", on_delete=models.SET_NULL, null=True, default=None)
    
    priority = models.IntegerField(default=0)  # 1-10, 1 being the highest
    # 0=new, 1=opened, 2=paused, 3=ignore, 4=resolved, 5=pending
    state = models.IntegerField(default=0, choices=INCIDENT_STATES)
    action_sent = models.DateTimeField(default=None, null=True)

    rule = models.ForeignKey("incident.Rule", on_delete=models.SET_NULL, null=True, default=None)

    @property
    def first_event(self):
        return self.events.first()

    @property
    def action_triggered(self):
        if self.rule is None or self.rule.action_after == 0:
            return True
        return self.events.all().count() >= abs(self.rule.action_after)

    @property
    def bundle_expired(self):
        if self.rule is not None:
            return self.created < (datetime.now() - timedelta(minutes=self.rule.bundle))
        return True

    def set_action(self, value):
        if value == "merge":
            request = self.getActiveRequest()
            ids = request.DATA.getList("merge_ids")
            if ids and len(ids) > 0:
                self.mergeWith(ids, request)
                self._changed__ = objict()

    def mergeWith(self, ids, request=None):
        qset = Incident.objects.filter(pk__in=ids).exclude(pk=self.pk)
        for incident in qset:
            self.logHistory(note=f"merged Incident #{incident.pk}", request=request, member=request.member)
            for event in incident.events.all():
                event.incident = self
                event.save()
            for h in self.history.all():
                h.parent = self
                h.save()
        qset.delete()
        count = self.events.all().count()
        self.setProperty("event_count", count)

    def updateMeta(self, event):
        for key in EVENT_META_TO_INCIDENT:
            if key in event.metadata:
                self.setProperty(key, event.metadata[key])
        self.setProperty("details", event.details)
        if event.metadata.geoip and event.metadata.geoip.city:
            self.setProperty("city", event.metadata.geoip.city)
            self.setProperty("state", event.metadata.geoip.state)
            self.setProperty("country", event.metadata.geoip.country)

    def shouldTriggerAction(self):
        count = self.events.all().count()
        self.setProperty("event_count", count)
        aa = self.rule.action_after
        if aa >= 0:
            return aa == count-1
        aa = abs(self.rule.action_after)
        return (count % aa) == 0

    def triggerAction(self, force=False):
        if self.rule is None:
            if self.action_sent is None:
                self.triggerAsyncNotify()
                self.triggerNotify()
            return
        # if self.rule.bundle == 0:
        #     return
        # only do query if not 0
        logger.info("triggerAction", self.rule.action)
        if force or self.shouldTriggerAction():
            logger.info(f"triggering incident action: {self.rule.action}")
            if self.state == INCIDENT_STATE_PENDING:
                self.state = INCIDENT_STATE_NEW
                self.save()
            self.triggerAsyncNotify()
            if self.rule.action is None or self.rule.action == "notify":
                self.triggerNotify()
            elif self.rule.action.startswith("email:") or self.rule.action.startswith("notify:"):
                self.triggerEmail()
            elif self.rule.action.startswith("sms:"):
                self.triggerSMS()
            elif self.rule.action.startswith("task:"):
                self.triggerTask()
            elif self.rule.action.startswith("group:"):
                self.triggerGroup()
            elif self.rule.action == "resolved":
                self.state = INCIDENT_STATE_RESOLVED
                self.save()
            elif self.rule.action.startswith("firewall_block"):
                if settings.FIREWALL_GLOBAL_BLOCK:
                    Task.Publish("incident", "firewall_block", 
                                 dict(ip=self.reporter_ip),
                                 channel="tq_broadcast")

    def triggerAsyncNotify(self):
        if self.lastSentAge() < 300:
            return
        msg = dict(
            pk=self.pk,
            created=time.mktime(self.created.timetuple()),
            description=self.description,
            category=self.category,
            component=self.component,
            component_id=self.component_id,
            hostname=self.hostname)
        if self.rule is not None:
            msg["rule"] = self.rule.name
        event = self.first_event
        if event is not None:
            msg["event_count"] = self.getProperty("event_count", default=1)
            msg["catagory"] = event.category
            msg["details"] = event.getProperty("details")
            msg["hostname"] = event.hostname
            msg["username"] = event.getProperty("username")
            msg["server"] = event.getProperty("server")
            msg["ip"] = event.getProperty("ip")
            msg["method"] = event.getProperty("method")
        if self.group is not None:
            msg["group_id"] = self.group.id
        try:
            ws4redis.sendMessageToPK("incident", "all", msg)
        except Exception:
            rh.log_exception("triggerAsyncNotify")

    def triggerTask(self):
        # task:APP_NAME:FNAME:CHANNEL
        fields = self.rule.action.split(':')
        if len(fields) < 4:
            rh.log_error("triggerTask failed, invalid field count")
            return
        self.action_sent = datetime.now()
        self.save()
        Task.Publish(fields[1], fields[2], channel=fields[3])

    def triggerEmail(self):
        if self.lastSentAge() < 300:
            return
        # email:NOTIFY_SETTING or email:bob@example.com
        action, perm = self.rule.action.split(":")
        self.action_sent = datetime.now()
        self.save()
        # notify with perm
        self.notifyWith(perm)

    def triggerSMS(self):
        if self.lastSentAge() < 300:
            return
        # sms:NOTIFY_SETTING
        self.action_sent = datetime.now()
        self.save()
        try:
            action, perm = self.rule.action.split(":")
            members = Member.GetWithNotification(perm)
            # count = self.getProperty("event_count", default=1, field_type=int)
            url = F"{settings.INCIDENT_PORTAL_URL}?incident={self.pk}"
            msg = f"Incident #{self.pk}\n{self.description}\n{url}"
            for m in members:
                m.sendSMS(msg)
        except Exception:
            rh.log_exception("triggerSMS")

    def triggerGroup(self):
        if not self.group:
            self.notifyWith("notify.unknown_incidents")
            return
        action, perm = self.rule.action.split(":")
        self.action_sent = datetime.now()
        self.save()

        subject = f"New Issue @ {self.group.name} - {self.description}"
        details = self.getProperty("details", self.description)
        username = self.getProperty("username", None)
        email = self.getProperty("email", None)
        phone = self.getProperty("phone", None)
        if self.category == "support":
            sms_msg = f"{settings.SITE_LABEL}\n{self.description}\n{details}"
        else:
            sms_msg = f"{settings.SITE_LABEL}\nIssue @ {self.group.name}\n{details}"

        body = []

        if username is not None:
            body.append(f"Reported by: {username}")
        if phone is not None:
            body.append(f"Requesting Callback: {phone}")
        elif email is not None:
            body.append(f"Respond to: {email}")
        body.append(f"Location: {self.group.name}")
        body.append("<hr>")
        body.append(f"<pre>{details}</pre>")
        if username is not None:
            body.append(f"- {username}")
        body = "<br>\n".join(body)
        # now we loop up through our groups parents
        count = 0
        group = self.group
        if perm.startswith("notify."):
            perm = perm.split(".")[1]
        sms_perms = f"notify.sms_{perm}"
        email_perms = f"notify.email_{perm}"
        while group is not None or count > 4:
            self.notifyMembers(group, subject, body, sms_msg, sms_perms, email_perms)
            group = group.parent

    def notifyMembers(self, group, subject, body, sms_msg, sms_perms, email_perms):
        members = group.getMembers(perms=sms_perms, as_member=True)
        for member in members:
            member.sendSMS(sms_msg)
        members = group.getMembers(perms=email_perms, as_member=True)
        for member in members:
            member.sendEmail(subject, body)       

    def notifyWith(self, perm):
        # logger.info("notifyWith", perm)
        count = self.getProperty("event_count", default=1, field_type=int)
        events = None
        if count > 1:
            subject = F"Incident #{self.pk} {self.category}@{self.hostname} had {count} events"
            events = self.events.all()
        else:
            subject = F"New Incident #{self.pk} {self.category}@{self.hostname}"

        Member.notifyWith(
            perm,
            subject=subject,
            template=settings.get("INCIDENT_TEMPLATE", "email/incident_plain.html"),
            context=dict(incident=self, portal_url=settings.INCIDENT_PORTAL_URL),
            email_only=True, from_email=INCIDENT_EMAIL_FROM)

    def lastSentAge(self):
        # prevent spams, only allow emails every 5 minutes
        if self.action_sent is None:
            return 100000
        return int((datetime.now() - self.action_sent).total_seconds())

    def triggerNotify(self):
        if self.lastSentAge() < 300:
            return
        self.action_sent = datetime.now()
        self.save()
        self.notifyWith("notify.unknown_incidents")

    def on_rest_saved(self, request, is_new=False):
        if not is_new:
            if self._changed__:
                self.logHistory(request=request)
            if request != None and len(request.FILES):
                for name, value in request.FILES.items():
                    self.logHistory(kind="media", media=value, request=request)
            if request != None and "DATA" in request and "note" in request.DATA:
                self.logHistory(kind="note", note=request.DATA.get("note"), request=request)

    def logHistory(self, kind="history", note=None, media=None, 
                   request=None, member=None, notify=True):
        if request is None:
            request = self.getActiveRequest()
        if member is None and request is not None and hasattr(request, "member"):
            member = request.member
        if note is None and self.has_model_changed:
            notes = []
            for k, v in self._changed__.items():
                nv = self.getFieldValue(k)
                notes.append(f"{k} changed from {v} to {nv}")
            note = "\n<br>".join(notes)

        h = IncidentHistory(
            parent=self,
            to=self.assigned_to,
            note=note,
            kind=kind,
            priority=self.priority,
            state=self.state)
        if member is not None:
            h.by = member
            if self.assigned_to is None:
                self.assigned_to = member
                self.save()
        if media is not None:
            h.saveMediaFile(media, "media", media.name)
        h.save()
        if notify and h.state != INCIDENT_STATE_IGNORE:
            self.notifyWatchers(
                subject=F"Updated Incident #{self.id}",
                history=h)

    def notifyWatchers(self, subject, history=None):
        action = None
        perm = "notify.incident_alerts"
        if self.rule is not None and (self.rule.action.startswith("email:") or self.rule.action.startswith("notify:")):
            action, perm = self.rule.action.split(":")
        context = dict(
                    incident=self,
                    portal_url=settings.INCIDENT_PORTAL_URL,
                    history=history)
        template = "email/incident_plain.html"

        # this should notify all users in our incident group of the change
        if self.group is not None:
            # all member of the group are notified because it is an incident group
            self.group.notifyMembers(
                subject=subject,
                template=template,
                context=context,
                perms=[perm],
                email_only=True,
                from_email=INCIDENT_EMAIL_FROM)
        elif history.by is None:
            # notify everyone with the perm
            Member.notifyWith(
                perm,
                subject,
                template=template,
                context=context,
                email_only=True,
                from_email=INCIDENT_EMAIL_FROM)
        else:
            # notitfy everyone but the sender          
            if history.by is None:
                members = Member.GetWithPermission(perm).exclude(pk=history.by.pk)
                if members.count() == 0:
                    return
                NotificationRecord = Incident.getModel("account", "NotificationRecord")
                NotificationRecord.notify(
                    members,
                    subject,
                    template=template,
                    context=context,
                    email_only=True,
                    from_email=INCIDENT_EMAIL_FROM)

    @classmethod
    def getBundled(cls, rule, event):
        # calculate our bundle start time
        when = datetime.now() - timedelta(minutes=rule.bundle)
        q = objict(rule=rule, created__gte=when)
        if rule.bundle_by in [2, 3, 5]:
            if event.component_id:
                q.component = event.component
                q.component_id = event.component_id
        if rule.bundle_by in [1, 3, 7]:
            q.hostname = event.hostname
        if rule.bundle_by in [4, 5, 8]:
            q.reporter_ip = event.reporter_ip
        if rule.bundle_by in [6, 7, 8]:
            q.category = event.category
        return Incident.objects.filter(**q).last()

    @classmethod
    def canPublishTo(cls, credentials, msg):
        if credentials:
            return True
        return False


class IncidentMetaData(rm.MetaDataBase):
    parent = models.ForeignKey(Incident, related_name="properties", on_delete=models.CASCADE)


class IncidentHistory(models.Model, rm.RestModel):
    class Meta:
        ordering = ['-created']

    class RestMeta:
        SEARCH_FIELDS = ["to__username", "note"]
        GRAPHS = {
            "default": {
                "extra":[
                    ("get_state_display", "state_display"),
                    ("get_priority_display", "priority_display"),
                ],
                "graphs":{
                    "by":"basic",
                    "to":"basic",
                    "media": "basic"
                }
            },
        }
    parent = models.ForeignKey(Incident, related_name="history", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    group = models.ForeignKey("account.Group", blank=True, null=True, default=None, related_name="+", on_delete=models.CASCADE)

    kind = models.CharField(max_length=80, blank=True, null=True, default=None, db_index=True)

    to = models.ForeignKey("account.Member", blank=True, null=True, default=None, related_name="+", on_delete=models.CASCADE)
    by = models.ForeignKey("account.Member", blank=True, null=True, default=None, related_name="+", on_delete=models.CASCADE)

    state = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)

    note = models.TextField(blank=True, null=True, default=None)
    media = models.ForeignKey("medialib.MediaItem", related_name="+", null=True, default=None, on_delete=models.CASCADE)

