from mfire.text.wind.const import ERROR_CASE
from mfire.text.wind.reducers.gust_summary_builder.gust_enum import GustCase
from mfire.text.wind.reducers.wind_summary_builder.helpers.wind_enum import WindCase

TEMPLATE_B1_1: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B1_2: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} s'orientant "
    "{{ wd_periods[1]['wd'] }} {{ wd_periods[1]['begin_time']|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }}."
)

TEMPLATE_B1_3: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ var_marker }} {{ wf_periods[1]['interval'][0] }} à "
    "{{ wf_periods[1]['interval'][1] }} {{ units }} "
    "{{ wf_periods[1]['begin_time']|safe }}."
)

TEMPLATE_B1_4: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "s'orientant {{ wd_periods[1]['wd'] }}, "
    "{{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ var_marker }} {{ wf_periods[1]['interval'][0] }} à "
    "{{ wf_periods[1]['interval'][1] }} {{ units }} "
    "{{ wf_periods[1]['begin_time']|safe }}."
)

TEMPLATE_B1_5: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ var_marker }} {{ wf_periods[1]['interval'][0] }} à "
    "{{ wf_periods[1]['interval'][1] }} {{ units }} "
    "avec une orientation {{ wd_periods[1]['wd']|safe }}"
    " {{ wf_periods[1]['begin_time']|safe }}."
)

TEMPLATE_B1_6: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B1_7: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "s'orientant {{ wd_periods[1]['wd']|safe }} "
    "{{ wd_periods[1]['begin_time']|safe }}, entre {{ wf_periods[0]['interval'][0] }} "
    "et {{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B1_8: str = (
    "Vent de {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B1_9: str = (
    "Vent de {{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }}, {{ var_marker }} {{ wf_periods[1]['interval'][0] }} à "
    "{{ wf_periods[1]['interval'][1] }} {{ units }} "
    "{{ wf_periods[1]['begin_time']|safe }}."
)

TEMPLATE_B1_10: str = (
    "Vent entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B2_1: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }}, {{ wf_periods[0]['time_desc']|safe }} ainsi que "
    "{{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_2: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wd_periods[0]['begin_time']|safe }} s'orientant {{ wd_periods[1]['wd']|safe }} "
    "{{ wd_periods[1]['begin_time']|safe }}."
)

TEMPLATE_B2_3: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }}, {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wd_periods[0]['time_desc']|safe }}."
)

TEMPLATE_B2_4: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }} "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}"
    " puis {{ wd_periods[1]['wd'] }}, et {{ wf_periods[1]['time_desc']|safe }} "
    "{{ wd_periods[2]['wd']|prefix_by_de_or_d|safe }}."
)

TEMPLATE_B2_5: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }} "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, et "
    "{{ wf_periods[1]['time_desc']|safe }} "
    "{{ wd_periods[1]['wd']|prefix_by_de_or_d|safe }} puis "
    "{{ wd_periods[2]['wd'] }}."
)

TEMPLATE_B2_6: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }} "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "puis {{ wd_periods[1]['wd'] }}, et "
    "{{ wf_periods[1]['time_desc']|safe }} "
    "{{ wd_periods[2]['wd']|prefix_by_de_or_d|safe }} "
    "puis {{ wd_periods[3]['wd'] }}."
)

TEMPLATE_B2_7: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }} {{ wf_periods[0]['time_desc']|safe }}, "
    "{{ wf_periods[1]['interval'][0] }} à {{ wf_periods[1]['interval'][1] }}"
    " {{ units }} {{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_8: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, "
    "{{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }} "
    " {{ units }} {{ wf_periods[0]['time_desc']|safe }}, puis "
    "{{ wf_periods[1]['interval'][0] }} à {{ wf_periods[1]['interval'][1] }} "
    " {{ units }} avec une orientation {{ wd_periods[1]['wd']|safe }} "
    "{{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_9: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} s'orientant "
    "{{ wd_periods[-1]['wd'] }}, {{ wf_periods[0]['interval'][0] }} à "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }}, "
    "{{ wf_periods[1]['interval'][0] }} à {{ wf_periods[1]['interval'][1] }}"
    " {{ units }} {{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_10: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, entre "
    "{{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B2_11: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wd_periods[0]['begin_time']|safe }} s'orientant {{ wd_periods[1]['wd']|safe }} "
    "{{ wd_periods[-1]['begin_time']|safe }}, entre "
    "{{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B2_12: str = (
    "Vent {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wd_periods[0]['time_desc']|safe }}, entre {{ wf_periods[0]['interval'][0] }} et"
    " {{ wf_periods[0]['interval'][1] }} {{ units }}."
)

TEMPLATE_B2_13: str = (
    "Vent entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }} "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} puis {{ wd_periods[1]['wd'] }}, "
    "et {{ wf_periods[1]['time_desc']|safe }} "
    "{{ wd_periods[2]['wd']|prefix_by_de_or_d|safe }}."
)

TEMPLATE_B2_14: str = (
    "Vent entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wf_periods[0]['time_desc']|safe }} "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}, et "
    "{{ wf_periods[1]['time_desc']|safe }} "
    "{{ wd_periods[1]['wd']|prefix_by_de_or_d|safe }} puis {{ wd_periods[2]['wd'] }}."
)

TEMPLATE_B2_15: str = (
    "Vent entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}, "
    "{{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wd_periods[0]['begin_time']|safe }} s'orientant "
    "{{ wd_periods[3]['wd'] }} {{ wd_periods[3]['begin_time']|safe }}."
)

TEMPLATE_B2_16: str = (
    "Vent {{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }} {{ wf_periods[0]['time_desc']|safe }}, "
    "{{ wf_periods[1]['interval'][0] }} à {{ wf_periods[1]['interval'][1] }}"
    " {{ units }} {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }} "
    "{{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_17: str = (
    "Vent de {{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }}, {{ wf_periods[0]['time_desc']|safe }} ainsi que "
    "{{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_18: str = (
    "Vent de {{ wf_periods[0]['interval'][0] }} à {{ wf_periods[0]['interval'][1] }}"
    " {{ units }} {{ wf_periods[0]['time_desc']|safe }}, "
    "{{ wf_periods[1]['interval'][0] }} à {{ wf_periods[1]['interval'][1] }}"
    " {{ units }} {{ wf_periods[1]['time_desc']|safe }}."
)

TEMPLATE_B2_19: str = (
    "Vent entre {{ wf_periods[0]['interval'][0] }} et "
    "{{ wf_periods[0]['interval'][1] }} {{ units }}."
)

ERROR_TEMPLATE: str = "Erreur dans la génération des synthèses de vent."


TEMPLATES_DICT: dict[str, str] = {
    GustCase.CASE_1.value: "",
    GustCase.CASE_2.value: (
        "Les rafales dépassent {% if gust_tempos[0] %}{{ gust_tempos[0]|safe }} "
        "{% endif %}les {{ force_min }} {{ units }}{% if gust_tempos[1] %} "
        "{{ gust_tempos[1]|safe }}{% endif %}. Valeurs maximales possibles entre "
        "{{ gust_interval[0] }} et {{ gust_interval[1] }} {{ units }}."
    ),
    WindCase.CASE_1.value: "",
    WindCase.CASE_2.value: (
        "Vent {{ wf_intensity }}{% if wd_periods|length > 0 %}"
        " {{ wd_periods[0]['wd']|prefix_by_de_or_d|safe }}{% endif %}"
        "{% if wd_periods|length == 2 %} s'orientant "
        "{{ wd_periods[1]['wd']|safe }} "
        "{{ wd_periods[1]['begin_time']|safe }}{% endif %}."
    ),
    WindCase.CASE_3_1B_1.value: TEMPLATE_B1_1,
    WindCase.CASE_3_1B_2.value: TEMPLATE_B1_2,
    WindCase.CASE_3_1B_3.value: TEMPLATE_B1_8,
    WindCase.CASE_3_1B_4.value: TEMPLATE_B1_3,
    WindCase.CASE_3_1B_5.value: TEMPLATE_B1_1,
    WindCase.CASE_3_1B_6.value: TEMPLATE_B1_4,
    WindCase.CASE_3_1B_7.value: TEMPLATE_B1_5,
    WindCase.CASE_3_1B_8.value: TEMPLATE_B1_2,
    WindCase.CASE_3_1B_9.value: TEMPLATE_B1_9,
    WindCase.CASE_3_1B_10.value: TEMPLATE_B1_8,
    WindCase.CASE_3_1B_11.value: TEMPLATE_B1_6,
    WindCase.CASE_3_1B_12.value: TEMPLATE_B1_7,
    WindCase.CASE_3_1B_13.value: TEMPLATE_B1_10,
    WindCase.CASE_3_2B_1.value: TEMPLATE_B2_1,
    WindCase.CASE_3_2B_2.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_3.value: TEMPLATE_B2_3,
    WindCase.CASE_3_2B_4.value: TEMPLATE_B2_3,
    WindCase.CASE_3_2B_5.value: TEMPLATE_B2_4,
    WindCase.CASE_3_2B_6.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_7.value: TEMPLATE_B2_5,
    WindCase.CASE_3_2B_8.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_9.value: TEMPLATE_B2_6,
    WindCase.CASE_3_2B_10.value: TEMPLATE_B2_17,
    WindCase.CASE_3_2B_11.value: TEMPLATE_B2_7,
    WindCase.CASE_3_2B_12.value: TEMPLATE_B2_1,
    WindCase.CASE_3_2B_13.value: TEMPLATE_B2_8,
    WindCase.CASE_3_2B_14.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_15.value: TEMPLATE_B2_7,
    WindCase.CASE_3_2B_16.value: TEMPLATE_B2_3,
    WindCase.CASE_3_2B_17.value: TEMPLATE_B2_16,
    WindCase.CASE_3_2B_18.value: TEMPLATE_B2_3,
    WindCase.CASE_3_2B_19.value: TEMPLATE_B2_9,
    WindCase.CASE_3_2B_20.value: TEMPLATE_B2_4,
    WindCase.CASE_3_2B_21.value: TEMPLATE_B2_9,
    WindCase.CASE_3_2B_22.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_23.value: TEMPLATE_B2_9,
    WindCase.CASE_3_2B_24.value: TEMPLATE_B2_5,
    WindCase.CASE_3_2B_25.value: TEMPLATE_B2_9,
    WindCase.CASE_3_2B_26.value: TEMPLATE_B2_2,
    WindCase.CASE_3_2B_27.value: TEMPLATE_B2_9,
    WindCase.CASE_3_2B_28.value: TEMPLATE_B2_6,
    WindCase.CASE_3_2B_29.value: TEMPLATE_B2_18,
    WindCase.CASE_3_2B_30.value: TEMPLATE_B2_17,
    WindCase.CASE_3_2B_31.value: TEMPLATE_B2_10,
    WindCase.CASE_3_2B_32.value: TEMPLATE_B2_11,
    WindCase.CASE_3_2B_33.value: TEMPLATE_B2_12,
    WindCase.CASE_3_2B_34.value: TEMPLATE_B2_12,
    WindCase.CASE_3_2B_35.value: TEMPLATE_B2_13,
    WindCase.CASE_3_2B_36.value: TEMPLATE_B2_11,
    WindCase.CASE_3_2B_37.value: TEMPLATE_B2_14,
    WindCase.CASE_3_2B_38.value: TEMPLATE_B2_11,
    WindCase.CASE_3_2B_39.value: TEMPLATE_B2_15,
    WindCase.CASE_3_2B_40.value: TEMPLATE_B2_19,
    ERROR_CASE: ERROR_TEMPLATE,
}
