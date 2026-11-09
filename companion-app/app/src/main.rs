use gloo_storage::{LocalStorage, Storage};
use gloo_timers::callback::Interval;
use leptos::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;

const CONTENT: &str = include_str!("../../content/v2.1-rc1/adventure.json");
const SAVE_KEY: &str = "dienstag-companion.session.v2";

#[derive(Clone, Debug, Deserialize)]
struct Adventure {
    title: String,
    subtitle: String,
    content_version: String,
    premise: String,
    safety: Vec<String>,
    schedule: Vec<ScheduleItem>,
    one_shot_schedule: Vec<ScheduleItem>,
    scenes: Vec<Scene>,
    countdowns: Vec<Countdown>,
    npcs: Vec<Npc>,
    adversaries: Vec<Adversary>,
    handouts: Vec<Handout>,
    endings: Vec<Ending>,
    quick_reference: Vec<QuickReference>,
}

#[derive(Clone, Debug, Deserialize)]
struct ScheduleItem {
    label: String,
    scene: String,
    purpose: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Scene {
    id: u8,
    title: String,
    location: String,
    duration_minutes: u16,
    goal: String,
    opening: String,
    beats: Vec<String>,
    clues: Vec<String>,
    moves: Vec<String>,
    cut: String,
    image: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Countdown {
    id: String,
    name: String,
    segments: u8,
    start: u8,
    ticks: String,
    full: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Npc {
    id: String,
    name: String,
    role: String,
    look: String,
    want: String,
    fear: String,
    voice: String,
    secret: String,
    question: String,
    portrait: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Adversary {
    id: String,
    name: String,
    role: String,
    difficulty: u8,
    thresholds: String,
    hp: u8,
    stress: u8,
    attack: String,
    damage: String,
    range: String,
    motives: String,
    features: Vec<String>,
    portrait: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Handout {
    id: String,
    number: u8,
    title: String,
    scene: u8,
    description: String,
    asset: String,
}

#[derive(Clone, Debug, Deserialize)]
struct Ending {
    name: String,
    opening: String,
    outcome: String,
    cost: String,
}

#[derive(Clone, Debug, Deserialize)]
struct QuickReference {
    when: String,
    then: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
struct EnemyTrack {
    hp: u8,
    stress: u8,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
struct SessionState {
    content_version: String,
    current_scene: u8,
    elapsed_seconds: u64,
    timer_running: bool,
    countdowns: HashMap<String, u8>,
    enemies: HashMap<String, EnemyTrack>,
    revealed_handouts: Vec<String>,
    scene_notes: HashMap<u8, String>,
    table_notes: String,
    mode: String,
}

impl Default for SessionState {
    fn default() -> Self {
        Self {
            content_version: "2.1-rc1".into(),
            current_scene: 1,
            elapsed_seconds: 0,
            timer_running: false,
            countdowns: HashMap::new(),
            enemies: HashMap::new(),
            revealed_handouts: Vec::new(),
            scene_notes: HashMap::new(),
            table_notes: String::new(),
            mode: "two-nights".into(),
        }
    }
}

fn fresh_state(adventure: &Adventure) -> SessionState {
    let mut state = SessionState {
        content_version: adventure.content_version.clone(),
        ..SessionState::default()
    };
    for countdown in &adventure.countdowns {
        state
            .countdowns
            .insert(countdown.id.clone(), countdown.start);
    }
    for enemy in &adventure.adversaries {
        state.enemies.insert(
            enemy.id.clone(),
            EnemyTrack {
                hp: enemy.hp,
                stress: 0,
            },
        );
    }
    state
}

fn load_state(adventure: &Adventure) -> SessionState {
    let Ok(state) = LocalStorage::get::<SessionState>(SAVE_KEY) else {
        return fresh_state(adventure);
    };
    if state.content_version == adventure.content_version {
        state
    } else {
        fresh_state(adventure)
    }
}

fn persist(state: &SessionState) {
    let _ = LocalStorage::set(SAVE_KEY, state);
}

fn update_state<F>(set_state: WriteSignal<SessionState>, update: F)
where
    F: FnOnce(&mut SessionState),
{
    set_state.update(|state| {
        update(state);
        persist(state);
    });
}

fn format_time(seconds: u64) -> String {
    let hours = seconds / 3600;
    let minutes = (seconds % 3600) / 60;
    let seconds = seconds % 60;
    format!("{hours:02}:{minutes:02}:{seconds:02}")
}

#[component]
fn CountdownPanel(
    countdowns: Vec<Countdown>,
    state: ReadSignal<SessionState>,
    set_state: WriteSignal<SessionState>,
) -> impl IntoView {
    view! {
        <div class="countdown-grid">
            {countdowns.into_iter().map(|countdown| {
                let id_minus = countdown.id.clone();
                let id_plus = countdown.id.clone();
                let id_value = countdown.id.clone();
                let id_dots = countdown.id.clone();
                let maximum = countdown.segments;
                let start = countdown.start;
                view! {
                    <article class="card countdown-card">
                        <div class="eyebrow">"OFFENE UHR · " {countdown.segments} " SEGMENTE"</div>
                        <h3>{countdown.name}</h3>
                        <div class="segment-row" aria-label="Countdown-Segmente">
                            {(0..countdown.segments).map(|index| {
                                let id = id_dots.clone();
                                view! {
                                    <span class:filled=move || { let value = state.get().countdowns.get(&id).copied().unwrap_or(start); value > index }></span>
                                }
                            }).collect_view()}
                        </div>
                        <div class="stepper">
                            <button class="small-button" on:click=move |_| {
                                update_state(set_state, |session| {
                                    let value = session.countdowns.entry(id_minus.clone()).or_insert(start);
                                    *value = value.saturating_sub(1);
                                });
                            } aria-label="Ein Segment entfernen">"−"</button>
                            <strong>{move || state.get().countdowns.get(&id_value).copied().unwrap_or(start)}</strong>
                            <button class="small-button" on:click=move |_| {
                                update_state(set_state, |session| {
                                    let value = session.countdowns.entry(id_plus.clone()).or_insert(start);
                                    *value = (*value + 1).min(maximum);
                                });
                            } aria-label="Ein Segment markieren">"+"</button>
                        </div>
                        <p><b>"Tickt: "</b>{countdown.ticks}</p>
                        <p class="danger"><b>"Voll: "</b>{countdown.full}</p>
                    </article>
                }
            }).collect_view()}
        </div>
    }
}

#[component]
fn Dashboard(
    adventure: Arc<Adventure>,
    state: ReadSignal<SessionState>,
    set_state: WriteSignal<SessionState>,
) -> impl IntoView {
    let quick = adventure.quick_reference.clone();
    let schedule = adventure.schedule.clone();
    let one_shot_schedule = adventure.one_shot_schedule.clone();
    let safety = adventure.safety.clone();
    view! {
        <section class="page-section">
            <div class="hero-panel">
                <div>
                    <div class="eyebrow">"SPIELLEITUNG · OFFLINE · RELEASEGEBUNDEN"</div>
                    <h1>{adventure.title.clone()}</h1>
                    <p class="subtitle">{adventure.subtitle.clone()}</p>
                    <p class="lead">{adventure.premise.clone()}</p>
                    <div class="hero-actions">
                        <span class="version-chip">"Inhalt " {adventure.content_version.clone()}</span>
                        <button class="ghost-button" on:click=move |_| {
                            update_state(set_state, |session| session.mode = if session.mode == "two-nights" { "one-shot".into() } else { "two-nights".into() });
                        }>{move || if state.get().mode == "two-nights" { "Modus: zwei Abende" } else { "Modus: One-Shot" }}</button>
                    </div>
                </div>
                <img src="/assets/illustrationen/cover.png" alt="Cover des Abenteuers" />
            </div>

            <div class="section-heading"><span>"01"</span><h2>"Offene Countdowns"</h2></div>
            <CountdownPanel countdowns=adventure.countdowns.clone() state set_state />

            <div class="two-column">
                <article class="card">
                    <div class="section-heading compact"><span>"02"</span><h2>"Zeitplan"</h2></div>
                    <div class="timeline">
                        {move || {
                            let items = if state.get().mode == "one-shot" { one_shot_schedule.clone() } else { schedule.clone() };
                            items.into_iter().map(|item| view! {
                                <div class="timeline-item">
                                    <time>{item.label}</time>
                                    <div><strong>{item.scene}</strong><small>{item.purpose}</small></div>
                                </div>
                            }).collect_view()
                        }}
                    </div>
                </article>
                <div class="stack">
                    <article class="card">
                        <div class="section-heading compact"><span>"03"</span><h2>"Wenn … dann …"</h2></div>
                        <dl class="quick-list">
                            {quick.into_iter().map(|item| view! {
                                <div><dt>{item.when}</dt><dd>{item.then}</dd></div>
                            }).collect_view()}
                        </dl>
                    </article>
                    <article class="card safety-card">
                        <div class="section-heading compact"><span>"04"</span><h2>"Sicherheit"</h2></div>
                        <ul>{safety.into_iter().map(|item| view! { <li>{item}</li> }).collect_view()}</ul>
                    </article>
                </div>
            </div>
        </section>
    }
}

#[component]
fn Scenes(
    scenes: Vec<Scene>,
    state: ReadSignal<SessionState>,
    set_state: WriteSignal<SessionState>,
) -> impl IntoView {
    let scenes_for_nav = scenes.clone();
    let scenes_for_body = scenes.clone();
    view! {
        <section class="page-section">
            <div class="page-title">
                <div><div class="eyebrow">"ABLAUF UND HARTE SCHNITTE"</div><h1>"Die acht Szenen"</h1></div>
                <div class="scene-picker">
                    {scenes_for_nav.into_iter().map(|scene| {
                        let id = scene.id;
                        view! {
                            <button class:active=move || state.get().current_scene == id on:click=move |_| update_state(set_state, |s| s.current_scene = id)>{id}</button>
                        }
                    }).collect_view()}
                </div>
            </div>
            {move || {
                let current = state.get().current_scene;
                let scene = scenes_for_body.iter().find(|scene| scene.id == current).cloned().unwrap_or_else(|| scenes_for_body[0].clone());
                let scene_id = scene.id;
                view! {
                    <article class="scene-sheet">
                        <header>
                            <div class="scene-number">{format!("{:02}", scene.id)}</div>
                            <div><div class="eyebrow">{scene.location.clone()} " · " {scene.duration_minutes} " MINUTEN"</div><h2>{scene.title.clone()}</h2><p>{scene.goal.clone()}</p></div>
                        </header>
                        <blockquote>{scene.opening.clone()}</blockquote>
                        <div class="scene-layout">
                            <div class="scene-copy">
                                <div class="note-block"><h3>"Szenenbeats"</h3><ul>{scene.beats.clone().into_iter().map(|x| view!{<li>{x}</li>}).collect_view()}</ul></div>
                                <div class="note-block clue"><h3>"Hinweise"</h3><ul>{scene.clues.clone().into_iter().map(|x| view!{<li>{x}</li>}).collect_view()}</ul></div>
                                <div class="note-block move"><h3>"GM Moves"</h3><ul>{scene.moves.clone().into_iter().map(|x| view!{<li>{x}</li>}).collect_view()}</ul></div>
                            </div>
                            <aside>
                                <img src=scene.image.clone() alt=format!("Illustration für Szene {}", scene.id) />
                                <div class="cut-box"><span>"HARTER SCHNITT"</span><p>{scene.cut.clone()}</p></div>
                                <label class="notes-label" for="scene-notes">"Notizen zu dieser Szene"</label>
                                <textarea id="scene-notes" rows="10"
                                    prop:value=move || state.get().scene_notes.get(&scene_id).cloned().unwrap_or_default()
                                    on:input=move |event| {
                                        let value = event_target_value(&event);
                                        update_state(set_state, |session| { session.scene_notes.insert(scene_id, value); });
                                    }
                                    placeholder="Was hat die Gruppe verändert? Welche Uhr trägt einen falschen Schnurrbart?"
                                ></textarea>
                            </aside>
                        </div>
                    </article>
                }.into_any()
            }}
        </section>
    }
}

#[component]
fn Npcs(npcs: Vec<Npc>) -> impl IntoView {
    let (query, set_query) = signal(String::new());
    view! {
        <section class="page-section">
            <div class="page-title">
                <div><div class="eyebrow">"STIMMEN, WÜNSCHE, WIDERSPRÜCHE"</div><h1>"NSC-Dossiers"</h1></div>
                <input class="search" type="search" placeholder="Person suchen …" on:input=move |event| set_query.set(event_target_value(&event)) />
            </div>
            <div class="portrait-grid">
                {move || {
                    let needle = query.get().to_lowercase();
                    npcs.iter().filter(|npc| format!("{} {} {}", npc.name, npc.role, npc.want).to_lowercase().contains(&needle)).cloned().map(|npc| view! {
                        <article class="portrait-card">
                            <img src=npc.portrait alt=format!("Portrait von {}", npc.name) />
                            <div class="portrait-body">
                                <div class="eyebrow">{npc.role}</div><h2>{npc.name}</h2><p>{npc.look}</p>
                                <dl><dt>"Will"</dt><dd>{npc.want}</dd><dt>"Fürchtet"</dt><dd>{npc.fear}</dd><dt>"Stimme"</dt><dd>{npc.voice}</dd><dt>"Spielwert"</dt><dd>{npc.secret}</dd></dl>
                                <blockquote>{npc.question}</blockquote>
                                <small class="id-label">{npc.id}</small>
                            </div>
                        </article>
                    }).collect_view()
                }}
            </div>
        </section>
    }
}

#[component]
fn Adversaries(
    adversaries: Vec<Adversary>,
    state: ReadSignal<SessionState>,
    set_state: WriteSignal<SessionState>,
) -> impl IntoView {
    view! {
        <section class="page-section">
            <div class="page-title"><div><div class="eyebrow">"TIER 1 · FLUCHT, VERHANDLUNG UND KAPITULATION SIND REGELKONFORM"</div><h1>"Gegner*innen"</h1></div></div>
            <div class="adversary-grid">
                {adversaries.into_iter().map(|enemy| {
                    let hp_minus = enemy.id.clone(); let hp_plus = enemy.id.clone(); let hp_read = enemy.id.clone();
                    let stress_minus = enemy.id.clone(); let stress_plus = enemy.id.clone(); let stress_read = enemy.id.clone();
                    let max_hp = enemy.hp; let max_stress = enemy.stress;
                    view! {
                        <article class="adversary-card">
                            <div class="enemy-top"><img src=enemy.portrait alt=format!("Portrait von {}", enemy.name) /><div><div class="eyebrow">{enemy.role}</div><h2>{enemy.name}</h2><p>{enemy.motives}</p></div></div>
                            <div class="stat-strip"><span><b>"SG"</b>{enemy.difficulty}</span><span><b>"Schwellen"</b>{enemy.thresholds}</span><span><b>"Angriff"</b>{enemy.attack}</span><span><b>"Schaden"</b>{enemy.damage}</span><span><b>"Reichweite"</b>{enemy.range}</span></div>
                            <div class="trackers">
                                <div><label>"HP"</label><button on:click=move |_| update_state(set_state, |s| { let t=s.enemies.entry(hp_minus.clone()).or_default(); t.hp=t.hp.saturating_sub(1); })>"−"</button><strong>{move || state.get().enemies.get(&hp_read).map(|x| x.hp).unwrap_or(max_hp)}</strong><span>"/" {max_hp}</span><button on:click=move |_| update_state(set_state, |s| { let t=s.enemies.entry(hp_plus.clone()).or_default(); t.hp=(t.hp+1).min(max_hp); })>"+"</button></div>
                                <div><label>"Stress"</label><button on:click=move |_| update_state(set_state, |s| { let t=s.enemies.entry(stress_minus.clone()).or_default(); t.stress=t.stress.saturating_sub(1); })>"−"</button><strong>{move || state.get().enemies.get(&stress_read).map(|x| x.stress).unwrap_or(0)}</strong><span>"/" {max_stress}</span><button on:click=move |_| update_state(set_state, |s| { let t=s.enemies.entry(stress_plus.clone()).or_default(); t.stress=(t.stress+1).min(max_stress); })>"+"</button></div>
                            </div>
                            <ul class="feature-list">{enemy.features.into_iter().map(|feature| view!{<li>{feature}</li>}).collect_view()}</ul>
                        </article>
                    }
                }).collect_view()}
            </div>
        </section>
    }
}

#[component]
fn Handouts(
    handouts: Vec<Handout>,
    state: ReadSignal<SessionState>,
    set_state: WriteSignal<SessionState>,
) -> impl IntoView {
    view! {
        <section class="page-section">
            <div class="page-title"><div><div class="eyebrow">"SPOILER WERDEN GEMEINSCHAFTLICH VERWALTET"</div><h1>"Handouts"</h1></div></div>
            <div class="handout-grid">
                {handouts.into_iter().map(|handout| {
                    let id_read = handout.id.clone(); let id_toggle = handout.id.clone();
                    let id_label = handout.id.clone();
                    let asset_for_when = handout.asset.clone();
                    let asset_for_image = handout.asset.clone();
                    view! {
                        <article class="handout-card">
                            <div class="handout-number">{format!("{:02}", handout.number)}</div>
                            <div class="eyebrow">"AB SZENE " {handout.scene}</div><h2>{handout.title}</h2><p>{handout.description}</p>
                            <Show when=move || !asset_for_when.is_empty()><img src=asset_for_image.clone() alt="Vorschau des Handouts" /></Show>
                            <button class:revealed=move || state.get().revealed_handouts.contains(&id_read) on:click=move |_| {
                                update_state(set_state, |session| {
                                    if let Some(position) = session.revealed_handouts.iter().position(|id| id == &id_toggle) { session.revealed_handouts.remove(position); }
                                    else { session.revealed_handouts.push(id_toggle.clone()); }
                                });
                            }>{move || if state.get().revealed_handouts.contains(&id_label) { "✓ Für Spielende freigegeben" } else { "Für Spielende freigeben" }}</button>
                        </article>
                    }
                }).collect_view()}
            </div>
        </section>
    }
}

#[component]
fn Endings(endings: Vec<Ending>) -> impl IntoView {
    view! {
        <section class="page-section">
            <div class="page-title"><div><div class="eyebrow">"NICHT DIE LÖSUNG, SONDERN EINE VERANTWORTETE ORDNUNG"</div><h1>"Mögliche Enden"</h1></div></div>
            <div class="ending-grid">{endings.into_iter().map(|ending| view!{
                <article class="card ending-card"><h2>{ending.name}</h2><p><b>"Öffnung · "</b>{ending.opening}</p><p><b>"Folge · "</b>{ending.outcome}</p><p class="cost"><b>"Preis · "</b>{ending.cost}</p></article>
            }).collect_view()}</div>
            <blockquote class="big-quote">"Wer entscheidet? Wer trägt die Kosten? Welche Stimme fehlt? Ein bittersüßes Ende ist willkommen; Zynismus ist oft nur Hoffnung mit einem schlecht sitzenden Schnurrbart."</blockquote>
        </section>
    }
}

#[component]
fn Notes(state: ReadSignal<SessionState>, set_state: WriteSignal<SessionState>) -> impl IntoView {
    view! {
        <section class="page-section notes-page">
            <div class="page-title"><div><div class="eyebrow">"LOKAL GESPEICHERT · KEINE CLOUD · KEIN CHRONOKONSORTIUM"</div><h1>"Sitzungsnotizen"</h1></div></div>
            <textarea rows="28" prop:value=move || state.get().table_notes on:input=move |event| {
                let value=event_target_value(&event); update_state(set_state, |session| session.table_notes=value);
            } placeholder="Entscheidungen, Versprechen, Beziehungen, offene Fragen …"></textarea>
            <p class="save-note">"Jede Änderung wird automatisch auf diesem Gerät gespeichert."</p>
        </section>
    }
}

#[component]
fn PlayerView(
    handouts: Vec<Handout>,
    state: ReadSignal<SessionState>,
    set_tab: WriteSignal<&'static str>,
) -> impl IntoView {
    view! {
        <section class="player-view">
            <header><div><div class="eyebrow">"SPIELENDENANSICHT"</div><h1>"Veyra erinnert sich"</h1></div><button on:click=move |_| set_tab.set("dashboard")>"Zur Spielleitung"</button></header>
            <img class="player-map" src="/assets/illustrationen/map_city_players_v1_0.png" alt="Spielendensichere Karte von Veyra" />
            <div class="revealed-grid">
                {move || {
                    let revealed=state.get().revealed_handouts;
                    handouts.iter().filter(|handout| revealed.contains(&handout.id)).cloned().map(|handout| {
                        let title_for_heading = handout.title.clone();
                        let title_for_alt = handout.title.clone();
                        let asset_for_when = handout.asset.clone();
                        let asset_for_image = handout.asset.clone();
                        view!{
                            <article><div class="eyebrow">"HANDOUT " {handout.number}</div><h2>{title_for_heading}</h2><p>{handout.description}</p><Show when=move || !asset_for_when.is_empty()><img src=asset_for_image.clone() alt=title_for_alt.clone() /></Show></article>
                        }
                    }).collect_view()
                }}
            </div>
        </section>
    }
}

#[component]
fn App() -> impl IntoView {
    let adventure: Adventure =
        serde_json::from_str(CONTENT).expect("Das Inhaltspaket v2.1-rc1 ist ungültig");
    let adventure = Arc::new(adventure);
    let initial = load_state(&adventure);
    let (state, set_state) = signal(initial);
    let (tab, set_tab) = signal("dashboard");

    let state_for_timer = state;
    Interval::new(1_000, move || {
        if state_for_timer.get_untracked().timer_running {
            update_state(set_state, |session| session.elapsed_seconds += 1);
        }
    })
    .forget();

    let a_dashboard = adventure.clone();
    let scenes = adventure.scenes.clone();
    let npcs = adventure.npcs.clone();
    let adversaries = adventure.adversaries.clone();
    let handouts = adventure.handouts.clone();
    let handouts_player = adventure.handouts.clone();
    let endings = adventure.endings.clone();
    let fresh_template = StoredValue::new(fresh_state(&adventure));
    let status_scenes = adventure.scenes.clone();
    let content_version = adventure.content_version.clone();
    let current_scene_title = Memo::new(move |_| {
        let id = state.get().current_scene;
        status_scenes
            .iter()
            .find(|scene| scene.id == id)
            .map(|scene| format!("{} · {}", scene.id, scene.title))
            .unwrap_or_default()
    });

    view! {
        <div class=move || if tab.get() == "player" { "app-shell player-mode" } else { "app-shell" }>
            <Show when=move || tab.get() != "player">
                <aside class="sidebar">
                    <div class="brand"><div class="clock-mark">"Ⅶ"</div><div><strong>"DIENSTAG"</strong><small>"COMPANION"</small></div></div>
                    <nav aria-label="Hauptnavigation">
                        <button class:active=move || tab.get()=="dashboard" on:click=move |_| set_tab.set("dashboard")><span>"⌂"</span>"Dashboard"</button>
                        <button class:active=move || tab.get()=="scenes" on:click=move |_| set_tab.set("scenes")><span>"八"</span>"Szenen"</button>
                        <button class:active=move || tab.get()=="npcs" on:click=move |_| set_tab.set("npcs")><span>"◉"</span>"NSCs"</button>
                        <button class:active=move || tab.get()=="adversaries" on:click=move |_| set_tab.set("adversaries")><span>"⚙"</span>"Gegner*innen"</button>
                        <button class:active=move || tab.get()=="handouts" on:click=move |_| set_tab.set("handouts")><span>"▤"</span>"Handouts"</button>
                        <button class:active=move || tab.get()=="endings" on:click=move |_| set_tab.set("endings")><span>"∞"</span>"Enden"</button>
                        <button class:active=move || tab.get()=="notes" on:click=move |_| set_tab.set("notes")><span>"✎"</span>"Notizen"</button>
                    </nav>
                    <button class="player-button" on:click=move |_| set_tab.set("player")>"Spielendenansicht öffnen"</button>
                    <div class="sidebar-footer"><span class="status-dot"></span>"Inhalt " {content_version.clone()}<small>"Quelle: Release · nicht main"</small></div>
                </aside>
                <header class="topbar">
                    <div class="scene-status"><span>"AKTUELLE SZENE"</span><strong>{move || current_scene_title.get()}</strong></div>
                    <div class="timer"><span>{move || format_time(state.get().elapsed_seconds)}</span><button on:click=move |_| update_state(set_state, |s| s.timer_running=!s.timer_running)>{move || if state.get().timer_running { "Pause" } else { "Start" }}</button><button class="icon-button" title="Timer zurücksetzen" on:click=move |_| update_state(set_state, |s| {s.elapsed_seconds=0;s.timer_running=false;})>"↺"</button></div>
                    <button class="reset-button" title="Alle Sitzungsdaten zurücksetzen" on:click=move |_| {
                        let fresh=fresh_template.get_value(); persist(&fresh); set_state.set(fresh);
                    }>"Neue Sitzung"</button>
                </header>
            </Show>
            <main>
                <Show when=move || tab.get()=="dashboard"><Dashboard adventure=a_dashboard.clone() state set_state /></Show>
                <Show when=move || tab.get()=="scenes"><Scenes scenes=scenes.clone() state set_state /></Show>
                <Show when=move || tab.get()=="npcs"><Npcs npcs=npcs.clone() /></Show>
                <Show when=move || tab.get()=="adversaries"><Adversaries adversaries=adversaries.clone() state set_state /></Show>
                <Show when=move || tab.get()=="handouts"><Handouts handouts=handouts.clone() state set_state /></Show>
                <Show when=move || tab.get()=="endings"><Endings endings=endings.clone() /></Show>
                <Show when=move || tab.get()=="notes"><Notes state set_state /></Show>
                <Show when=move || tab.get()=="player"><PlayerView handouts=handouts_player.clone() state set_tab /></Show>
            </main>
        </div>
    }
}

fn main() {
    mount_to_body(App);
}
