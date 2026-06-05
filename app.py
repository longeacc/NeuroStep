import streamlit as st
import database as db



st.set_page_config(
    page_title="Catalogue - Cérébrolésés / Tumeur",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .header-light {
        color: #555;
        font-weight: 300;
        font-size: 1.2rem;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .top-right-note {
        color: #2e86de;
        font-style: italic;
        text-align: right;
        font-size: 0.9rem;
    }
    .app-card {
        border: 1px solid #e0e0e0; border-radius: 12px;
        padding: 18px; margin-bottom: 12px;
        background: #fafafa;
    }
    .tag { display: inline-block; background: #e8f4f8; color: #1a5276;
           padding: 2px 10px; border-radius: 12px; font-size: 0.82rem;
           margin: 2px 3px; }
</style>
""", unsafe_allow_html=True)


col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<p class="header-light">Cérébrolésés / Tumeur</p>', unsafe_allow_html=True)
    st.title("Catalogue numérique API / Outils")
with col2:
    st.markdown('<p class="top-right-note">Outil déjà créé<br>Améliorer l\'outil</p>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown("## Perspective")
    perspective = st.radio("Mode d'affichage", ["Utilisateur", "ADMIN"])
    
    st.markdown("---")
    st.markdown("### Thème d'activité")
    themes = db.get_all_themes()
    for theme in themes:
        st.markdown(f"- {theme}")



st.subheader(" Recherche d'API / Logiciels")

col_search, col_os, col_tr = st.columns(3)

with col_search:
    search_query = st.text_input("Rechercher (nom ou description)...")

with col_os:
    os_choice = st.selectbox("Support (OS)", ["Tous", "iOS", "Android", "Web", "Windows"])

with col_tr:
    troubles = db.get_all_troubles()
    trouble_choice = st.selectbox("Rechercher par pathologie (Trouble)", ["Tous"] + troubles)

st.markdown("---")

apps = db.get_all_apps()

# Filtrage Global
filtered_apps = []
for app in apps:
    if os_choice != "Tous" and os_choice not in app.get("plateformes", []):
        continue
    if trouble_choice != "Tous" and trouble_choice not in app.get("troubles", []):
        continue
    if search_query:
        q = search_query.lower()
        if (q not in app.get("nom", "").lower() and q not in app.get("description", "").lower()):
            continue
    filtered_apps.append(app)


if perspective == "Utilisateur":
    st.markdown("### Logiciels existants (API)")
    
    if not filtered_apps:
        st.warning("Aucun outil trouvé pour ces critères.")
    
    for app in filtered_apps:
        with st.container():
            enrichi_badge = " Fichier enrichi" if app.get("enrichi") else ""
            gratuit_badge = " Gratuit" if app.get("gratuit") else " Payant"
            
            tags_html = "".join([f'<span class="tag">{tr}</span>' for tr in app.get("troubles", [])])
            link_html = f"<br><br><a href='{app.get('url_store')}' target='_blank'> Voir l'outil</a>" if app.get("url_store") else ""

            # Image à gauche, dans l'encadré gris (vide si pas d'image)
            image_html = ""
            if app.get("image"):
                image_html = f"<img src='{app.get('image')}' alt='{app.get('nom')}' style='width: 280px; object-fit: cover; border-radius: 8px; flex-shrink: 0;'/>"

            # HTML sans indentation pour éviter que Streamlit l'interprète comme un bloc de code
            card_html = (
                '<div class="app-card" style="display: flex; gap: 16px; align-items: flex-start;">'
                '<div style="flex: 1; min-width: 0;">'
                f'<h4 style="margin-top: 0;">{app.get("nom")}</h4>'
                '<div style="color: #666; font-size: 0.9em; margin-bottom: 10px;">'
                f'{", ".join(app.get("plateformes", []))}  ·  {gratuit_badge}  ·  {enrichi_badge}'
                '</div>'
                f'<p>{app.get("description", "").replace(chr(10), "<br>")}</p>'
                f'<div>{tags_html}</div>'
                f'{link_html}'
                '</div>'
                f'{image_html}'
                '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

elif perspective == "ADMIN":
    st.subheader(" Administration & Enrichissement")
    
    st.markdown("**Note:** Nécessite de tester les API (Avantage / Inconvénient).")
    
    tab_list, tab_add = st.tabs([f"Fichiers existants ({len(filtered_apps)})", "Ajouter un outil [+]"])
    
    with tab_list:
        if not filtered_apps:
            st.warning("Aucun outil trouvé pour ces critères.")

        # Affichage des cards sous forme de formulaire accordéon interactif
        for app in filtered_apps:
            label_titre = f"{app.get('nom')} - {' Enrichi' if app.get('enrichi') else ' À enrichir'}"
            with st.expander(label_titre):
                with st.form(f"edit_form_{app.get('id')}"):
                    edit_nom = st.text_input("Nom de l'API / Outil", value=app.get("nom", ""))
                    edit_desc = st.text_area("Avantages / Inconvénients / Description", value=app.get("description", ""))
                    edit_image = st.text_input("URL de l'image (logo / capture)", value=app.get("image", ""))
                    
                    all_os = ["iOS", "Android", "Web", "Windows"]
                    current_os = [x for x in app.get("plateformes", []) if x in all_os]
                    edit_os = st.multiselect("Supports", all_os, default=current_os)
                    
                    all_troubles = db.get_all_troubles()
                    current_troubles = [x for x in app.get("troubles", []) if x in all_troubles]
                    edit_troubles = st.multiselect("Troubles ciblés", all_troubles, default=current_troubles)
                    
                    c1, c2 = st.columns(2)
                    edit_gratuit = c1.checkbox("Est-ce gratuit ?", value=app.get("gratuit", False))
                    edit_enrichi = c2.checkbox("Fichier enrichi (Amélioré) ?", value=app.get("enrichi", False))
                    
                    if st.form_submit_button(" Sauvegarder les modifications"):
                        db.update_app(app.get("id"), {
                            "nom": edit_nom,
                            "description": edit_desc,
                            "image": edit_image,
                            "plateformes": edit_os,
                            "gratuit": edit_gratuit,
                            "enrichi": edit_enrichi,
                            "troubles": edit_troubles
                        })
                        st.success("Modifications enregistrées avec succès !")
                        st.rerun()

    with tab_add:
        # Formulaire d'ajout
        with st.form("add_app_form"):
            new_nom = st.text_input("Nom de l'API / Outil")
            new_desc = st.text_area("Avantages / Inconvénients / Description")
            new_image = st.text_input("URL de l'image (logo / capture)")
            new_os = st.multiselect("Supports", ["iOS", "Android", "Web", "Windows"])
            new_gratuit = st.checkbox("Est-ce gratuit ?")
            new_troubles = st.multiselect("Troubles ciblés", db.get_all_troubles())
            
            if st.form_submit_button("Ajouter l'outil [+]"):
                if new_nom:
                    db.insert_app({
                        "nom": new_nom,
                        "description": new_desc,
                        "image": new_image,
                        "plateformes": new_os,
                        "gratuit": new_gratuit,
                        "troubles": new_troubles,
                        "enrichi": False
                    })
                    st.success("Outil ajouté avec succès dans la base JSON !")
                    st.rerun()
                else:
                    st.error("Le nom de l'application est obligatoire.")