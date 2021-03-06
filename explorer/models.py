from explorer.utils import passes_blacklist, write_csv, swap_params, execute_query, execute_and_fetch_query, extract_params, shared_dict_update
from django.db import models, DatabaseError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

MSG_FAILED_BLACKLIST = "Query failed the SQL blacklist."


class Query(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    sql = models.TextField(null=True, blank=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    last_run_date = models.DateTimeField(auto_now=True)
    query_editor = models.BooleanField(default=False)
    table =  models.TextField(null=True, blank=True)
    columns = models.TextField(null=True, blank=True)
    rows =  models.TextField(null=True, blank=True)
    obs_values =  models.TextField(null=True, blank=True)
    aggregations =  models.TextField(null=True, blank=True)
    filters =  models.TextField(null=True, blank=True)
    agg_filters =  models.TextField(null=True, blank=True)
    include_code = models.BooleanField(default=False)
    open_data = models.BooleanField(default=False)

    params = {}

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Queries'

    def __unicode__(self):
        return unicode(self.title)

    def passes_blacklist(self):
        return passes_blacklist(self.final_sql())

    def final_sql(self):
        return swap_params(self.sql, self.params)

    def csv_report(self):
        headers, data, duration, error = self.headers_and_data()
        if error:
            return error
        return write_csv(headers, data)

    def error_messages(self):
        if not self.passes_blacklist():
            return MSG_FAILED_BLACKLIST
        try:
            execute_query(self.final_sql())
            return None
        except DatabaseError, e:
            return str(e)

    def headers_and_data(self):
        if not self.passes_blacklist():
            return [], [], None, MSG_FAILED_BLACKLIST
        try:
            return execute_and_fetch_query(self.final_sql())
        except (DatabaseError, Warning), e:
            return [], [], None, str(e)

    def available_params(self):
        p = extract_params(self.sql)
        if self.params:
            shared_dict_update(p, self.params)
        return p

    def get_absolute_url(self):
        return reverse("query_detail", kwargs={'query_id': self.id})