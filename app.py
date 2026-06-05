"""
app.py — Neurostep : Plateforme de compensation des fonctions cognitives
────────────────────────────────────────────────────────────────────────
Lancement : streamlit run app.py
"""

import streamlit as st
import database as db
import search_engine as se

# ═══════════════════════════════════════════════════════════════════
# CONFIG STREAMLIT
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Neurostep",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Init DB si nécessaire
db.init_db()

# CSS custom
st.markdown("""
<style>
    .score-badge {
        text-align: center; padding: 14px 8px; border-radius: 10px;
        color: white; font-weight: 700; font-size: 1.3rem;
    }
    .score-high { background: #27ae60; }
    .score-mid  { background: #f39c12; }
    .score-low  { background: #e74c3c; }
    .app-card {
        border: 1px solid #e0e0e0; border-radius: 12px;
        padding: 18px; margin-bottom: 12px;
        background: #fafafa;
    }
    .tag { display: inline-block; background: #e8f4f8; color: #1a5276;
           padding: 2px 10px; border-radius: 12px; font-size: 0.82rem;
           margin: 2px 3px; }
    .fn-tag { background: #eaf2e3; color: #2d6a2e; }
    .header-stat {
        text-align: center; padding: 15px;
        border-radius: 10px; background: #f8f9fa;
    }
    .rgpd-footer {
        text-align: center; color: #999; font-size: 0.75rem;
        padding: 20px 0 10px 0; border-top: 1px solid #eee; margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — Navigation
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("##  Neurostep")
    st.caption("Compensation des fonctions cognitives")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Recherche", " Catalogue", "Patients", "Statistiques"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Stats rapides
    n_apps = db.count_apps()
    n_patients = len(db.get_all_patients())
    st.metric("Applications", n_apps)
    st.metric("Patients suivis", n_patients)

    st.markdown("---")
    st.caption("Données 100 % locales")
    st.caption("Aucune transmission externe")
    st.caption(" Aide à la sélection — ne remplace pas le jugement clinique")


# ═══════════════════════════════════════════════════════════════════
# FONCTION UTILITAIRE : Score badge
# ═══════════════════════════════════════════════════════════════════

def score_badge(pct: float) -> str:
    css = "score-high" if pct >= 70 else "score-mid" if pct >= 45 else "score-low"
    return f'<div class="score-badge {css}">{pct}%</div>'


def stars(n: float | None) -> str:
    if not n:
        return "☆ Pas encore évalué"
    full = int(round(n))
    return "⭐" * full + "☆" * (5 - full) + f" ({n:.1f}/5)"


# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — RECHERCHE SÉMANTIQUE
# ═══════════════════════════════════════════════════════════════════

if "Recherche" in page:
    st.title("Recherche sémantique")
    st.markdown(
        "Décrivez librement le profil cognitif ou le besoin de votre patient. "
        "Le moteur comprend le langage clinique."
    )

    # Barre de recherche
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input(
            "Requête",
            placeholder="ex : patient AVC avec troubles de mémoire prospective et fatigabilité",
            label_visibility="collapsed",
        )
    with col_btn:
        clicked = st.button("Chercher", use_container_width=True)

    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        pf = st.selectbox("Plateforme", ["Toutes", "iOS", "Android", "Web", "iPad"])
    with col_f2:
        gratuit_only = st.checkbox("Gratuit uniquement")
    with col_f3:
        fonctions = db.get_all_fonctions()
        fn_opts = [{"id": None, "nom": "Toutes les fonctions"}] + fonctions
        fn_sel = st.selectbox(
            "Fonction cognitive",
            fn_opts,
            format_func=lambda x: x["nom"],
        )

    # Parcourir par catégorie
    if not query:
        st.markdown("---")
        st.subheader("Ou parcourir par catégorie")
        cats = db.get_categories()
        cat_emojis = {
            "attention": "🎯", "mémoire": "🧩", "exécutif": "⚙️",
            "langage": "💬", "visuo-spatial": "👁️", "praxies": "✋",
        }
        cols = st.columns(min(len(cats), 3))
        for i, cat in enumerate(cats):
            with cols[i % 3]:
                emoji = cat_emojis.get(cat, "🔹")
                if st.button(f"{emoji} {cat.capitalize()}", use_container_width=True, key=f"cat_{cat}"):
                    query = cat
                    clicked = True

    # Résultats
    if query:
        with st.spinner("Recherche sémantique en cours..."):
            results = se.search(
                query, k=15,
                plateforme=pf if pf != "Toutes" else None,
                gratuit_only=gratuit_only,
                fonction_id=fn_sel["id"] if fn_sel["id"] else None,
            )

        if not results:
            st.warning("Aucun résultat. Essayez une reformulation ou élargissez les filtres.")
        else:
            st.success(f"**{len(results)} résultats** pour : *{query}*")

            for r in results:
                with st.container():
                    st.markdown('<div class="app-card">', unsafe_allow_html=True)
                    c1, c2 = st.columns([5, 1])

                    with c1:
                        gratuit_label = "💶 Gratuit" if r["gratuit"] else f"💰 {r.get('prix_eur', '?')} €"
                        st.markdown(f"### {r['nom']}")
                        st.caption(f"📱 {r['plateforme']}  ·  {gratuit_label}  ·  {stars(r.get('score_moyen'))}")

                        # Tags fonctions cognitives
                        if r.get("fonctions"):
                            tags = "".join(
                                f'<span class="tag fn-tag">{fn.strip()}</span>'
                                for fn in r["fonctions"].split("·")
                            )
                            st.markdown(tags, unsafe_allow_html=True)

                        # Phrase la plus pertinente
                        expl = se.explain_match(query, r["description"])
                        st.caption(f'*"...{expl["best_sentence"][:150]}..."*')

                    with c2:
                        st.markdown(score_badge(r["score_pct"]), unsafe_allow_html=True)
                        st.caption("Pertinence")

                        if st.button("Voir →", key=f"see_{r['id']}"):
                            st.session_state["view_app_id"] = r["id"]
                            st.session_state["page_override"] = "fiche"
                            st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — CATALOGUE (+ Fiche détaillée)
# ═══════════════════════════════════════════════════════════════════

elif "Catalogue" in page or st.session_state.get("page_override") == "fiche":

    # ── Fiche détaillée d'une application ────────────────────────
    view_id = st.session_state.get("view_app_id")

    if view_id:
        app = db.get_app_by_id(view_id)
        if app:
            if st.button("← Retour au catalogue"):
                st.session_state.pop("view_app_id", None)
                st.session_state.pop("page_override", None)
                st.rerun()

            st.title(f"🧩 {app['nom']}")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Plateforme", app["plateforme"])
            with c2:
                prix = "Gratuit" if app["gratuit"] else f"{app.get('prix_eur', '?')} €"
                st.metric("Prix", prix)
            with c3:
                sm = app.get("score_moyen")
                st.metric("Note moyenne", f"{sm:.1f}/5" if sm else "—")

            st.markdown("---")
            st.subheader("Description")
            st.write(app["description"])

            if app.get("objectif_ther"):
                st.subheader("Objectif thérapeutique")
                st.info(app["objectif_ther"])

            # Fonctions cognitives
            fns = db.get_fonctions_for_app(view_id)
            if fns:
                st.subheader("Fonctions cognitives ciblées")
                for fn in fns:
                    icon = "●" if fn["intensite"] == "principale" else "○"
                    st.markdown(f"  {icon}  **{fn['nom']}** ({fn['categorie']}) — {fn['description']}")

            # Lien
            if app.get("url_store"):
                st.link_button("🔗 Ouvrir dans le store", app["url_store"])

            # Évaluations
            st.markdown("---")
            evals = db.get_evaluations_for_app(view_id)
            st.subheader(f"Évaluations cliniques ({len(evals)})")

            if evals:
                for ev in evals:
                    with st.expander(
                        f"{stars(ev['score_global'])} — {ev['evaluateur_type']} · {ev['date_eval'][:10]}"
                    ):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Facilité", f"{ev['facilite_usage']}/5" if ev['facilite_usage'] else "—")
                        c2.metric("Pertinence", f"{ev['pertinence_ther']}/5" if ev['pertinence_ther'] else "—")
                        c3.metric("Accessibilité", f"{ev['accessibilite']}/5" if ev['accessibilite'] else "—")
                        if ev.get("commentaire"):
                            st.write(ev["commentaire"])
            else:
                st.caption("Aucune évaluation pour le moment.")

            # Formulaire d'évaluation
            st.markdown("---")
            with st.expander("➕ Ajouter mon évaluation"):
                with st.form(f"eval_form_{view_id}"):
                    ev_type = st.radio("Vous êtes :", ["ergo", "patient", "etudiant"], horizontal=True)
                    ev_global = st.slider("Score global", 1, 5, 4)
                    ev_facil = st.slider("Facilité d'usage", 1, 5, 3)
                    ev_pert = st.slider("Pertinence thérapeutique", 1, 5, 3)
                    ev_acc = st.slider("Accessibilité cognitive", 1, 5, 3)
                    ev_comment = st.text_area("Commentaire")
                    ev_ctx = st.text_input("Contexte d'utilisation (optionnel)")

                    if st.form_submit_button("Soumettre"):
                        db.add_evaluation(
                            view_id, ev_type, ev_global,
                            ev_facil, ev_pert, ev_acc,
                            ev_comment, ev_ctx,
                        )
                        st.success("Évaluation enregistrée !")
                        st.rerun()

            # Ajouter au suivi d'un patient
            patients = db.get_all_patients()
            if patients:
                st.markdown("---")
                with st.expander("📋 Ajouter au suivi d'un patient"):
                    pat_sel = st.selectbox(
                        "Patient",
                        patients,
                        format_func=lambda p: f"{p['alias'] or 'Patient'} #{p['id']}",
                    )
                    freq = st.text_input("Fréquence (ex: 3x/semaine 15 min)")
                    notes = st.text_input("Notes")
                    if st.button("Ajouter au suivi"):
                        db.add_suivi(pat_sel["id"], view_id, freq, notes)
                        st.success(f"Ajouté au suivi de #{pat_sel['id']}")

        else:
            st.error("Application non trouvée.")
    else:
        # ── Liste du catalogue ───────────────────────────────────
        st.title("📂 Catalogue des applications")

        apps = db.get_all_apps()
        if not apps:
            st.warning("Aucune application dans la base. Lancez `python generate_seed_data.py`.")
        else:
            # Filtre par catégorie
            cats = ["Toutes"] + db.get_categories()
            cat_filter = st.selectbox("Filtrer par catégorie", cats)

            for app in apps:
                # Filtre
                if cat_filter != "Toutes":
                    fns = app.get("fonctions", "") or ""
                    # Check via DB
                    app_fns = db.get_fonctions_for_app(app["id"])
                    if not any(f["categorie"] == cat_filter for f in app_fns):
                        continue

                with st.container():
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        gratuit_label = "💶 Gratuit" if app["gratuit"] else f"💰 {app.get('prix_eur', '?')} €"
                        st.markdown(f"**{app['nom']}** — 📱 {app['plateforme']} · {gratuit_label}")
                        if app.get("fonctions"):
                            st.caption(f"🧠 {app['fonctions']}")
                    with c2:
                        if st.button("Voir", key=f"cat_{app['id']}"):
                            st.session_state["view_app_id"] = app["id"]
                            st.rerun()
                    st.markdown("---")


# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — PATIENTS
# ═══════════════════════════════════════════════════════════════════

elif "Patients" in page:
    st.title("👤 Gestion des patients")

    tab_list, tab_new = st.tabs(["Liste des patients", "Nouveau patient"])

    # ── Nouveau patient ──────────────────────────────────────────
    with tab_new:
        st.subheader("Créer un profil patient")
        st.caption("Aucune donnée nominative n'est stockée. Un identifiant pseudonymisé est généré automatiquement.")

        with st.form("new_patient"):
            alias = st.text_input("Alias (optionnel)", placeholder="ex: Patient mémoire #3")
            profil = st.text_area(
                "Profil lésionnel",
                placeholder="ex: AVC ischémique droit, hémiplégie gauche, fatigabilité modérée",
            )

            fonctions = db.get_all_fonctions()
            fn_selected = st.multiselect(
                "Fonctions cognitives atteintes",
                fonctions,
                format_func=lambda f: f"{f['nom']} ({f['categorie']})",
            )
            notes = st.text_area("Notes générales", placeholder="Informations complémentaires")

            if st.form_submit_button("Créer le patient"):
                fn_ids = ",".join(str(f["id"]) for f in fn_selected)
                pid = db.create_patient(alias, profil, fn_ids, notes)
                st.success(f"Patient créé avec l'identifiant **#{pid}**")
                st.rerun()

    # ── Liste des patients ───────────────────────────────────────
    with tab_list:
        patients = db.get_all_patients()

        if not patients:
            st.info("Aucun patient enregistré.")
        else:
            for pat in patients:
                with st.expander(f"👤 {pat.get('alias') or 'Patient'} — #{pat['id']}"):
                    st.caption(f"Créé le {pat['date_creation']}")

                    if pat.get("profil_lesionnel"):
                        st.markdown(f"**Profil lésionnel :** {pat['profil_lesionnel']}")

                    if pat.get("fonctions_atteintes"):
                        fn_ids = [int(x) for x in pat["fonctions_atteintes"].split(",") if x.strip()]
                        all_fns = db.get_all_fonctions()
                        fn_map = {f["id"]: f for f in all_fns}
                        fn_names = [fn_map[fid]["nom"] for fid in fn_ids if fid in fn_map]
                        if fn_names:
                            tags = " · ".join(fn_names)
                            st.markdown(f"**Fonctions atteintes :** {tags}")

                    if pat.get("notes_generales"):
                        st.markdown(f"**Notes :** {pat['notes_generales']}")

                    # Suivis
                    suivis = db.get_suivis_for_patient(pat["id"])
                    if suivis:
                        st.markdown("**Outils en cours de suivi :**")
                        for s in suivis:
                            status_emoji = {
                                "en_cours": "🟢", "terminé": "✅",
                                "suspendu": "⏸️", "abandonné": "🔴"
                            }.get(s["statut"], "⚪")

                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.markdown(
                                    f"{status_emoji} **{s['app_nom']}** — "
                                    f"depuis {s['date_debut']} · {s.get('frequence', '')}"
                                )
                                if s.get("notes"):
                                    st.caption(s["notes"])
                            with col2:
                                if s.get("progression"):
                                    st.markdown(f"Progression : {'⭐' * s['progression']}")
                            with col3:
                                new_status = st.selectbox(
                                    "Statut",
                                    ["en_cours", "terminé", "suspendu", "abandonné"],
                                    index=["en_cours", "terminé", "suspendu", "abandonné"].index(s["statut"]),
                                    key=f"status_{s['id']}",
                                )
                                if new_status != s["statut"]:
                                    db.update_suivi(s["id"], statut=new_status)
                                    st.rerun()
                    else:
                        st.caption("Aucun outil suivi pour ce patient.")

                    # Recherche adaptée
                    if st.button(f"🔍 Trouver un outil pour ce patient", key=f"search_{pat['id']}"):
                        search_query = pat.get("profil_lesionnel", "")
                        if pat.get("fonctions_atteintes"):
                            fn_ids = [int(x) for x in pat["fonctions_atteintes"].split(",") if x.strip()]
                            all_fns = db.get_all_fonctions()
                            fn_map = {f["id"]: f for f in all_fns}
                            fn_names = [fn_map[fid]["nom"] for fid in fn_ids if fid in fn_map]
                            search_query += " " + " ".join(fn_names)
                        st.session_state["prefill_query"] = search_query.strip()
                        st.info(f"→ Recherchez avec : *{search_query.strip()}*")


# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — STATISTIQUES
# ═══════════════════════════════════════════════════════════════════

elif "Statistiques" in page:
    st.title("📊 Vue d'ensemble")

    apps = db.get_all_apps()
    patients = db.get_all_patients()
    fonctions = db.get_all_fonctions()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Applications", len(apps))
    c2.metric("Fonctions cognitives", len(fonctions))
    c3.metric("Patients", len(patients))

    conn = db.get_connection()
    n_evals = conn.execute("SELECT COUNT(*) FROM evaluations").fetchone()[0]
    conn.close()
    c4.metric("Évaluations", n_evals)

    st.markdown("---")

    # Répartition par catégorie
    st.subheader("Applications par catégorie cognitive")
    conn = db.get_connection()
    cat_data = conn.execute("""
        SELECT fc.categorie, COUNT(DISTINCT af.app_id) AS n
        FROM app_fonctions af
        JOIN fonctions_cognitives fc ON fc.id = af.fonction_id
        GROUP BY fc.categorie
        ORDER BY n DESC
    """).fetchall()
    conn.close()

    if cat_data:
        import pandas as pd
        df_cat = pd.DataFrame([dict(r) for r in cat_data])
        st.bar_chart(df_cat.set_index("categorie"))

    # Répartition gratuit/payant
    st.subheader("Gratuit vs Payant")
    n_gratuit = sum(1 for a in apps if a["gratuit"])
    n_payant = len(apps) - n_gratuit

    c1, c2 = st.columns(2)
    c1.metric("💶 Gratuit", n_gratuit)
    c2.metric("💰 Payant", n_payant)

    # Top apps par évaluation
    st.subheader("Applications les mieux évaluées")
    conn = db.get_connection()
    top_apps = conn.execute("""
        SELECT a.nom, AVG(e.score_global) AS score, COUNT(e.id) AS n_eval
        FROM evaluations e
        JOIN applications a ON a.id = e.app_id
        GROUP BY a.id
        HAVING n_eval >= 1
        ORDER BY score DESC
        LIMIT 10
    """).fetchall()
    conn.close()

    if top_apps:
        for ta in top_apps:
            st.markdown(f"  {stars(ta['score'])}  **{ta['nom']}** ({ta['n_eval']} éval.)")
    else:
        st.caption("Pas encore d'évaluations.")


# ═══════════════════════════════════════════════════════════════════
# FOOTER RGPD
# ═══════════════════════════════════════════════════════════════════

st.markdown(
    '<div class="rgpd-footer">'
    '🔒 Neurostep — Toutes les données restent sur votre appareil. '
    'Aucune donnée personnelle n\'est transmise à un serveur externe.<br>'
    '⚖️ Cet outil est une aide à la sélection et ne remplace pas le jugement clinique du professionnel.<br>'
    'Hackathon SN@SU 2026 — Clément Longeac — ESIEE Paris / DuraXELL'
    '</div>',
    unsafe_allow_html=True,
)
