import streamlit as st
from supabase import create_client, Client
from datetime import date

st.set_page_config(
    page_title="Reserva de Salas",
    page_icon="📅",
    layout="centered"
)

@st.cache_resource
def conectar_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = conectar_supabase()

st.title("📅 Reserva de Salas - UTFPR")

salas = [
    "Sala 101",
    "Sala 102",
    "Laboratório 1",
    "Laboratório 2",
    "Sala de Reuniões"
]

horarios = [
    "08:15 - 10:00",
    "10:15 - 12:00",
    "13:30 - 15:20",
    "15:30 - 17:20",
    "18:45 - 20:25",
    "20:35 - 22:15"
]

sala = st.selectbox("Escolha a sala:", salas)
data_reserva = st.date_input("Escolha a data:", min_value=date.today())

st.subheader("Horários")

resultado = (
    supabase.table("reservas")
    .select("*")
    .eq("sala", sala)
    .eq("data", data_reserva.isoformat())
    .execute()
)

reservas = resultado.data
horarios_ocupados = {r["horario"]: r for r in reservas}

for horario in horarios:
    if horario in horarios_ocupados:
        reserva = horarios_ocupados[horario]
        st.error(f"{horario} — Reservado por {reserva['professor']}")
    else:
        with st.expander(f"🟢 {horario} — Livre"):
            professor = st.text_input(
                "Nome do professor:",
                key=f"professor_{horario}"
            )

            disciplina = st.text_input(
                "Disciplina:",
                key=f"disciplina_{horario}"
            )

            observacao = st.text_area(
                "Observação:",
                key=f"obs_{horario}"
            )

            if st.button("Reservar", key=f"botao_{horario}"):
                if not professor.strip():
                    st.warning("Digite o nome do professor.")
                else:
                    try:
                        supabase.table("reservas").insert({
                            "sala": sala,
                            "data": data_reserva.isoformat(),
                            "horario": horario,
                            "professor": professor.strip(),
                            "disciplina": disciplina.strip(),
                            "observacao": observacao.strip()
                        }).execute()

                        st.success("Reserva realizada com sucesso!")
                        st.rerun()

                    except Exception as e:
                        st.error("Não foi possível realizar a reserva.")
                        st.write(e)

st.divider()

st.subheader("Reservas do dia")

if reservas:
    for r in reservas:
        st.write(
            f"**{r['horario']}** — {r['professor']} "
            f"({r.get('disciplina') or 'Sem disciplina informada'})"
        )
else:
    st.info("Nenhuma reserva para essa sala nesta data.")
