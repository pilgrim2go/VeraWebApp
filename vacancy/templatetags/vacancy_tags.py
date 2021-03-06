from django import template

from jobboard.handlers.oracle import OracleHandler
from jobboard.models import Specialisation, Keyword
from member_profile.models import Schedule, Busyness, Profile
from vacancy.models import MemberOnVacancy

register = template.Library()

CHANGE_FILTERS = {'specialisation': 'specialisations', 'keyword': 'keywords', 'salary': 'salary_from'}


@register.inclusion_tag('vacancy/tags/job_with_count.html')
def get_jobs_with(item, type_s, _list):
    if _list is '' or not _list:
        count = 0
    else:
        if type_s == 'spec':
            count = _list.filter(specialisations__in=[item, ]).count()
        elif type_s == 'keyword':
            count = _list.filter(keywords__in=[item, ]).count()
        elif type_s == 'salary':
            if isinstance(_list[0], Profile):
                count = _list.filter(position__salary_from__gte=item).count()
            else:
                count = _list.filter(salary_from__gte=item).count()
        elif type_s == 'busyness':
            if isinstance(_list[0], Profile):
                count = _list.filter(position__busyness__in=[item, ]).count()
            else:
                count = _list.filter(busyness__in=[item, ]).count()
        elif type_s == 'schedule':
            if isinstance(_list[0], Profile):
                count = _list.filter(position__schedule__in=[item, ]).count()
            else:
                count = _list.filter(schedule__in=[item, ]).count()
        else:
            count = 0
    return {'count': count}


@register.filter(name='get_filter_url')
def get_filter_url(get_dict, item):
    need_key = get_real_filter_name(item.__class__.__name__.lower())
    query_str = '?'
    query_list = ['{}={}'.format(need_key, item.pk)]
    for key, value in get_dict.items():
        if key == need_key:
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    add_filter_param(query_list)
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_salary_url')
def get_salary_url(get_dict, salary):
    query_str = '?'
    query_list = ['salary_from={}'.format(salary)]
    for key, value in get_dict.items():
        if key == 'salary_from':
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    add_filter_param(query_list)
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_custom_url')
def get_custom_url(get_dict, item):
    query_str = '?'
    query_list = ['{}={}'.format(item['type'], item['id'])]
    for key, value in get_dict.items():
        if key == item['type']:
            pass
        else:
            query_list.append('{}={}'.format(key, value))
    query_str += '&'.join(query_list)
    return query_str


@register.filter(name='get_clear_url')
def get_clear_url(get_dict, item):
    if len(get_dict) > 0:
        query_str = '?'
        query_list = []
        if not isinstance(item, str):
            need_key = get_real_filter_name(item.__class__.__name__.lower())
        else:
            need_key = item

        for key, value in get_dict.items():
            if key == need_key:
                pass
            else:
                query_list.append('{}={}'.format(key, value))
        arr = list(set(get_dict.keys()) - {'sort', 'period', 'page'})
        arr.remove(need_key)
        if len(arr) == 1 and arr[0] == 'filter':
            query_list.remove('filter=true')
        query_str += '&'.join(query_list)
        return query_str
    else:
        return ''


@register.inclusion_tag('vacancy/tags/filter.html', takes_context=True)
def get_filter(context):
    request = context.request
    filt = {}
    for item in context:
        if 'all' in item:
            filt['all'] = item['all']
    filt['salary_range'] = [i * 1000 for i in range(1, 9)]
    specialisations = Specialisation.objects.all()
    keywords = Keyword.objects.all()
    busyness = Busyness.objects.all()
    schedule = Schedule.objects.all()
    if 'specialisations' in request.GET:
        filt['selected_spec'] = specialisations.filter(pk=request.GET.get('specialisations')).first()
        filt['specialisations'] = specialisations.filter(parent_specialisation=filt['selected_spec'])
    else:
        filt['specialisations'] = specialisations.filter(parent_specialisation=None)
    if 'keywords' in request.GET:
        filt['selected_keyword'] = keywords.filter(pk=request.GET.get('keywords')).first()
    else:
        filt['keywords'] = keywords
    if 'salary_from' in request.GET:
        filt['selected_salary'] = request.GET.get('salary_from')
    if 'busyness' in request.GET:
        filt['selected_busyness'] = busyness.filter(pk=request.GET.get('busyness')).first()
    else:
        filt['busyness'] = busyness
    if 'schedule' in request.GET:
        filt['selected_schedule'] = schedule.filter(pk=request.GET.get('schedule')).first()
    else:
        filt['schedule'] = schedule
    filt.update({'request': request})
    return filt


def add_filter_param(query_list):
    if 'filter=true' not in query_list:
        return query_list.append('filter=true')
    return query_list


def get_real_filter_name(need_key):
    if need_key in CHANGE_FILTERS:
        return CHANGE_FILTERS[need_key]
    return need_key


@register.filter
def get_interview_fee(vacancy):
    return '-'.join([str(i.chain.fee) for i in vacancy.pipeline.actions.all()])


@register.filter
def may_apply_vacancy(member, vacancy):
    if not member.contract_address:
        return False
    oracle = OracleHandler()
    current_action_index = oracle.get_member_current_action_index(vacancy.company.contract_address, vacancy.uuid,
                                                                  member.contract_address)
    already_subscribed = MemberOnVacancy.objects.filter(member=member, vacancy=vacancy).exists()
    return current_action_index == -1 and not already_subscribed
