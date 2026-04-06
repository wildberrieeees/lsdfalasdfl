import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import tempfile
import os

from pandas import DataFrame
from plotly.subplots import make_subplots

st.title("Аналитическая справка по результатам входного контроля учащихся 5-11 классов 👩‍🎓👨‍🎓", text_alignment="center")

sub = {}
not_passed_w = []
SCORES = ["НБ-2", "БУ-3", "ПУ-4", "ВУ-5"]
ACAP = "Академическая успеваемость"
ACAQ = "Академическое качество"
last_klass = 0


def get_one_subject_acap_acaq_at_klass(school_data, klass: str, subject: str):
    data = []
    acap = 0
    acaq = 0
    lens = 0
    data.append({})
    for i in school_data:
        if i.replace("(СТАРТ)", "") == subject:
            for z in school_data[i]:
                if klass in z["КЛАСС"]:
                    acap += z["Академическая успеваемость"]
                    acaq += z["Академическое качество"]
                    lens += 1

    return {"name": subject, 'values': [acap / lens, acaq / lens]}


def get_all_start_control(school_data):
    """"
    Функция для получения всех элементов основного массива,
    переданного в аргументы данной функции, содержащих ключ "Стартовый контроль" со значением True.
    Иными словами, функция получает те классы, в которых был проведён стартовый контроль.
    """
    data = []
    for i in school_data:
        for v in school_data[i]:
            if v["Стартовый контроль"] is True:
                data.append(v)
    return data


def get_all_students_in_class(school_all):
    """"
    Функция для подсчёта общего количества обучающихся во всех классах,
    учитывая то, что в классе может быть разделение на две и более группы по какому-либо предмету.
    Ничего не возвращает и заносит в основной словарь данные по классам.
    В случае, когда в классе имеются две и более группы, в словарь дополнительно добавляется ключ '2GROUPS' со значением True;
    в ином случае ключа не будет вовсе, по причине ненадобности в общей статистике в будущем.
    """
    z = 0
    for index, i in enumerate(school_all):
        peoples = 0
        for index1, s in enumerate(school_all[i]):
            if s.__getitem__("НБ-2") == "Не сдан учителем" or s.__getitem__("НБ-2") == "Не" or s.__getitem__(
                    "НБ-2") == "сдано":
                not_passed_w.append({"КЛАСС": s["КЛАСС"], "Преподаватель": s["Преподаватель"]})
            else:
                for score in SCORES:
                    if type(s.__getitem__(score)) is int:
                        pass
                    else:
                        peoples += int(str(s.__getitem__(score)).split("/")[0])

                sub[list(sub)[index]][index1].setdefault("ОБУЧАЮЩИХСЯ", peoples)
                peoples = 0
        z += 1


def academic_performance_with_quality(school_all):
    """"
    Функция для подсчёта академической, то есть общей успеваемости класса по каждому предмету, по определённой формуле.
    Кроме того, функция определяет качество знаний по каждому классу конкретного предмета.
    Использовать СТРОГО после использования функции get_all_students_in_class.
    Академическая успеваемость и качество знаний будут занесены в основной словарь
    с ключами Академическая успеваемость и Академическое качество соответственно.
    """
    z = 0
    for index, i in enumerate(school_all):

        for index1, s in enumerate(school_all[i]):
            if s.__getitem__("НБ-2") == "Не сдан учителем" or s.__getitem__("НБ-2") == "Не" or s.__getitem__(
                    "НБ-2") == "сдано":
                not_passed_w.append({"КЛАСС": s["КЛАСС"], "Преподаватель": s["Преподаватель"]})
            else:
                academic_quality = (int(str(s.__getitem__("ПУ-4")).split("/")[0]) + int(
                    str(s.__getitem__("ВУ-5")).split("/")[0]))
                academic_performance = academic_quality + int(str(s.__getitem__("БУ-3")).split("/")[0])
                sub[list(sub)[index]][index1].setdefault(ACAQ,
                                                         round(academic_quality / int(s.__getitem__("ОБУЧАЮЩИХСЯ")),
                                                               2) * 100)
                sub[list(sub)[index]][index1].setdefault(ACAP,
                                                         round(academic_performance / int(s.__getitem__("ОБУЧАЮЩИХСЯ")),
                                                               2) * 100)
        z += 1


last_subject = ""
start_control = False


def parse_data(df: DataFrame):
    global last_subject, last_klass, start_control
    for index, row in df.iterrows():

        if not row["Unnamed: 7"] == "сданы":
            if row["Класс"] != "nan" and "nan" not in str(row["Учитель"]):
                iteration = 0
                klass = 0
                data = {}
                if str(row["Предмет"]) != "nan":
                    last_subject = str(row["Предмет"]).replace("\n", "").upper()
                    sub.setdefault(last_subject, [])
                for i in row.values:
                    if "nan" not in str(i) and last_subject != str(i).replace("\n", "").upper():

                        if iteration.__eq__(0):
                            klass = str(i).split("\n")[0]
                            if len(str(klass)) <= 4:
                                data.__setitem__("КЛАСС", klass)
                                last_klass = klass
                            else:
                                data.__setitem__("КЛАСС", last_klass)

                            sub[last_subject].append(data)
                        if len(str(klass)) <= 4:
                            if iteration.__eq__(1):
                                data.__setitem__("Преподаватель", i)
                            if iteration.__eq__(2):
                                data.__setitem__("НБ-2", i)
                            if iteration.__eq__(3):
                                data.__setitem__("БУ-3", i)
                            if iteration.__eq__(4):
                                data.__setitem__("ПУ-4", i)
                            if iteration.__eq__(5):
                                data.__setitem__("ВУ-5", i)
                                if type(i) is float and i == 0.0:
                                    data.__setitem__("ВУ-5", 0)
                        else:
                            if iteration.__eq__(0):
                                data.__setitem__("Преподаватель", i)
                            if iteration.__eq__(1):
                                data.__setitem__("НБ-2", i)
                            if iteration.__eq__(2):
                                data.__setitem__("БУ-3", i)
                            if iteration.__eq__(3):
                                data.__setitem__("ПУ-4", i)
                            if iteration.__eq__(4):
                                if type(i) is float:
                                    if i != 0.0:
                                        data.__setitem__("2GROUP", True)
                                    elif i == 0.0:
                                        data.__setitem__("ВУ-5", 0)

                                        continue

                                data.__setitem__("ВУ-5", i)

                        iteration += 1

                iteration = 0
                if start_control is True:
                    data.__setitem__("Стартовый контроль", True)
                else:
                    data.__setitem__("Стартовый контроль", False)

            else:
                if str(row["Предмет"]) != "nan":
                    if "класс" in str(row["Предмет"]):
                        if "СТАРТ" in str(row["Предмет"]):
                            start_control = True
                        else:
                            start_control = False
        for index, i in enumerate(sub):
            if "СТАРТ" in i:
                for index1, v in enumerate(sub[i]):
                    sub[list(sub)[index]][index1].__setitem__("Стартовый контроль", True)


def get_all_start_control(school_data):
    data = {}
    for i in school_data:
        data.__setitem__(str(i.replace("(СТАРТ)", "")), [])
    for i in school_data:
        for v in school_data[i]:
            if v["Стартовый контроль"] is True:
                data[str(i.replace("(СТАРТ)", ""))].append(v["КЛАСС"])

    return data


def get_one_subject_data(school_data, subject: str):
    ''''
    Получение данных из массива по одному из предметов.
    '''
    return school_data[subject]


def get_one_class_data(school_data, st_control: bool, klass: str):
    ''''
    Получение данных из массива по одному из классов. Учитывается является ли работа стартовой аргументом st_control
    '''
    data = []
    for i in school_data:
        if i["Стартовый контроль"] is st_control:
            if list(i["КЛАСС"])[1].isdigit():
                if i["КЛАСС"] == klass:
                    data.append(i)
            else:
                if list(i["КЛАСС"])[0] == klass:
                    data.append(i)
    return data


def get_all_acap_acaq_at_klass(school_data, klass, st_control):
    ''''
    Получение общей академической успеваемости и качества обучения в классе.
    st_control указывает на какие работы стоит смотреть. st_control = true -> стартовые, st_control = false = входные
    '''
    data = []
    for index, i in enumerate(school_data):
        acap = 0
        acaq = 0
        lens = 0
        data.append({})
        for z in school_data[i]:
            if list(z["КЛАСС"])[0] == klass:
                if z["Стартовый контроль"] is st_control:
                    try:
                        acap += z["Академическая успеваемость"]
                        acaq += z["Академическое качество"]
                        lens += 1
                    except Exception:
                        pass
                else:
                    continue
            else:
                if z["КЛАСС"] == klass:
                    try:
                        acap += z["Академическая успеваемость"]
                        acaq += z["Академическое качество"]
                        lens += 1
                    except Exception:
                        pass
        if lens == 0:
            continue

        print(f"ACAP - {acap / lens} ACAQ - {acaq / lens}")
        data[index].__setitem__("name", str(i).replace("(СТАРТ)", ""))
        data[index].__setitem__("values", [acap / lens, acaq / lens])
        acap = 0
        acaq = 0
        lens = 0
    return [item for item in data if item]


def calculate_sizes(data, base_height=200, base_width=300):
    ''''
    Расчет размера для создания графиков
    '''
    cols = 3
    rows = (len(data) + cols - 1) // cols
    total_height = base_height * rows + 50
    total_width = base_width * cols
    return total_height, total_width


try:
    df = pd.read_excel(st.file_uploader("Выберите файл", type=["xlsx"]))
except Exception:
    st.subheader("Выберите файл для аналитического отчета в формате *.XLSX", text_alignment="center")
else:
    st.subheader("Файл загружен!")
    parse_data(df)
    get_all_students_in_class(sub)
    academic_performance_with_quality(sub)
    st.subheader("Стартовые контрольные работы выполняли:")
    all_start = get_all_start_control(sub)
    with st.expander(""):
        display_option = st.radio(
            "Способ отображения:",
            ["По предметам (предметы в строках)", "По классам (классы в строках)"],
            horizontal=True
        )
        if display_option == "По предметам (предметы в строках)":
            st.subheader("Предметы и соответствующие классы")

            rows = []
            for subject, classes in all_start.items():
                unique_classes = sorted(set(classes))
                rows.append({
                    "Предмет": subject,
                    "Классы": ", ".join(unique_classes),
                    "Количество классов": len(unique_classes)
                })

            df_subjects = pd.DataFrame(rows)
            st.dataframe(df_subjects, use_container_width=True, hide_index=True)

        elif display_option == "По классам (классы в строках)":
            st.subheader("Классы и преподаваемые в них предметы")


            all_classes = set()
            for classes in all_start.values():
                all_classes.update(classes)
            sorted_classes = sorted(all_classes, key=lambda x: (
                int(x[:-1]) if x[:-1].isdigit() else 999,
                x[-1] if len(x) > 1 else ''
            ))

            rows = []
            for class_name in sorted_classes:
                subjects_for_class = []
                for subject, classes in all_start.items():
                    if class_name in classes:
                        subjects_for_class.append(subject)

                if subjects_for_class:
                    rows.append({
                        "Класс": class_name,
                        "Предметы": ", ".join(subjects_for_class),
                        "Количество предметов": len(subjects_for_class)
                    })

            df_classes = pd.DataFrame(rows)
            st.dataframe(df_classes, use_container_width=True, hide_index=True)
    st.subheader("Общий анализ результатов по классам и предметам")
    with st.expander("Стартовый контроль"):
        with st.expander("Стартовые работы 5 класс"):
            st.subheader("Стартовые работы 5 класса")
            data = get_all_acap_acaq_at_klass(sub, "5", True)

            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=10),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )
            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': False, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_5_class"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_5_class",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )

        data = 0
        with st.expander("Стартовые работы 6-8 классов"):
            st.subheader(" Стартовый контроль 6-8 классы")
            data = [get_one_subject_acap_acaq_at_klass(sub, "6", "ОБЩЕСТВОЗНАНИЕ"),
                    get_one_subject_acap_acaq_at_klass(sub, "7", "ФИЗИКА"),
                    get_one_subject_acap_acaq_at_klass(sub, "8", "ХИМИЯ")]
            ata = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=10),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )
            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': False, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)

            if st.button("Скачать график как изображение", key="download_6_8_classes"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_6_8_classes",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
        with st.expander("Стартовый контроль - 10 класс"):
            st.subheader("Стартовый контроль - 10 класс")
            data = get_all_acap_acaq_at_klass(sub, "10", True)

            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )
            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_10_class"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_10_class",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )

    with st.expander("Входные контрольные работы"):
        with st.expander("6 Класс"):
            data = get_all_acap_acaq_at_klass(sub, "6", False)
            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )

            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_6_class_input"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_6_class_input",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
        with st.expander("7 Класс"):
            data = get_all_acap_acaq_at_klass(sub, "7", False)
            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )

            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_7_class_input"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_7_class_input",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
        with st.expander("8 Класс"):
            data = get_all_acap_acaq_at_klass(sub, "8", False)
            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )

            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_8_class_input"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_8_class_input",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
        with st.expander("9 Класс"):
            data = get_all_acap_acaq_at_klass(sub, "9", False)
            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )

            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_9_class_input"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_9_class_input",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
        with st.expander("11 Класс"):
            data = get_all_acap_acaq_at_klass(sub, "11", False)
            data = [item for item in data if item['values']]

            cols = 3
            rows = (len(data) + cols - 1) // cols
            height, width = calculate_sizes(data)

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles="",
                horizontal_spacing=0.05,
                vertical_spacing=0.1
            )

            for i, group in enumerate(data):
                row = i // cols + 1
                col = i % cols + 1
                fig.add_trace(
                    go.Bar(
                        x=['Общая усп.', 'Качество'],
                        y=group['values'],
                        name=f"Значения {group['name']}",
                        showlegend=True,
                        text=group['values'],
                        textposition='inside',
                        texttemplate='%{text:.1f}',
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=height,
                width=width,
                showlegend=True,
                font=dict(size=10),
                margin=dict(l=0, r=0, t=10, b=0),
                autosize=False
            )
            fig.update_xaxes(
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Общая усп.', 'Качество'],
                row=row, col=col
            )

            fig.update_yaxes(automargin=False, ticklen=5, anchor="free")

            config = {'scrollZoom': True, 'displayModeBar': False}
            st.plotly_chart(fig, config=config, width=width, height=height)
            if st.button("Скачать график как изображение", key="download_11_class_input"):
                export_width = 1200
                export_height = 800

                fig_temp = fig.update_layout(
                    template="plotly",
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    width=export_width,
                    height=export_height
                )
                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    fig_temp.write_html(tmp.name)
                    img_bytes = pio.to_image(fig_temp, format='png', engine='kaleido')

                st.download_button(
                    key="png_11_class_input",
                    label="Скачать PNG",
                    data=img_bytes,
                    file_name="График.png",
                    mime="image/png"
                )
    st.subheader("Не были сданы работы")
    with st.expander(""):
        df = pd.DataFrame(not_passed_w)
        df_clean = df.drop_duplicates()
        grouping_option = st.radio(
            "Группировать по:",
            ["По классу", "По преподавателю"],
            horizontal=True
        )
        if grouping_option == "По классу":
            st.subheader("Группировка по классам")
            sorted_df = df_clean.sort_values("КЛАСС")
            st.dataframe(sorted_df, use_container_width=True, hide_index=True)
        elif grouping_option == "По преподавателю":
            st.subheader("Группировка по преподавателям")
            grouped = df_clean.groupby("Преподаватель")["КЛАСС"].apply(
                lambda x: ", ".join(sorted(set(x)))).reset_index()
            grouped.columns = ["Преподаватель", "КЛАССЫ"]
            st.dataframe(grouped, use_container_width=True, hide_index=True)
