use serde::Serialize;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct BootstrapState {
    schema_version: &'static str,
    truth_policy: &'static str,
    baseline_sha: &'static str,
    working_branch: &'static str,
    phase: &'static str,
    network_mode: &'static str,
    notification_capability: &'static str,
}

#[tauri::command]
fn get_bootstrap_state() -> BootstrapState {
    BootstrapState {
        schema_version: "2.0.0",
        truth_policy: "legacy-provisional",
        baseline_sha: "9e15068d453284e027cf6413ef9fc2871ee17f70",
        working_branch: "project-owners/master-critical-path-v1",
        phase: "ontology-normalization",
        network_mode: "local-only",
        notification_capability: "native-plugin",
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_notification::init())
        .invoke_handler(tauri::generate_handler![get_bootstrap_state])
        .run(tauri::generate_context!())
        .expect("error while running Master Critical Path");
}
