// Small helpers shared by the LVGL lambdas.
#pragma once

#include <algorithm>
#include <string>
#include <vector>
#include <esp_wifi.h>
#include "esphome/components/wifi/wifi_component.h"
#include "esphome/core/helpers.h"

// A driven entity is lit when it is not off: switches say "on", climates "heat"/"cool"...
inline bool is_on(const std::string &s) {
  return !s.empty() && s != "off" && s != "unavailable" && s != "unknown" && s != "idle";
}

// Is now_min inside [from_min, to_min)? All three are minutes since midnight.
// The window may wrap past midnight (e.g. 23:00 -> 07:00), which is the normal
// case for a night schedule, so a plain from <= now < to would be wrong.
inline bool time_in_window(int now_min, int from_min, int to_min) {
  if (from_min == to_min)
    return false;                       // empty window = never
  if (from_min < to_min)
    return now_min >= from_min && now_min < to_min;
  return now_min >= from_min || now_min < to_min;
}

// ------------------------------------------------------------------ wifi scan
// The settings page lists the networks the board can actually see, so nobody
// has to type an SSID exactly right.
//
// Deliberately NOT WiFiComponent::start_scanning(): that puts the component
// into STA_SCANNING, which drops the association and reconnects afterwards.
// esp_wifi_scan_start() leaves the connection alone - the radio just goes
// off-channel for a couple of seconds - and ESPHome's own WIFI_EVENT_SCAN_DONE
// handler fills scan_result_ either way. It only keeps the FULL list when
// keep_scan_results_ is set; without it we would get just the networks matching
// the configured SSID, which is the one we already know about.
inline void wifi_scan_begin() {
  esphome::wifi::global_wifi_component->set_keep_scan_results(true);
  esp_err_t err = esp_wifi_scan_start(nullptr, false);   // non-blocking
  if (err != ESP_OK)
    ESP_LOGW("wifi_scan", "scan not started: %s", esp_err_to_name(err));
}

// The results as dropdown options, strongest first (ESPHome sorts them), with
// `manual` appended last - the caller relies on "last entry = type it by hand".
// Never returns an empty vector: LvSelectable::set_options() does
// `options.size() - 1` on a size_t and would wrap.
//
// LvSelectable::set_options() now takes FixedVector<const char *> and keeps
// it (get_options()/get_selected_text() read it back later), so the pointers
// have to stay valid after this function returns - a local std::vector<std::string>
// would dangle. `storage` is static so its buffers outlive the call; each
// scan overwrites it, which is fine since set_options() replaces the widget's
// whole option list synchronously right after this returns.
// ponytail: static storage means only the latest scan's strings are valid -
// fine for one dropdown reused one at a time; give it per-widget storage if a
// second scanning dropdown is ever added.
inline esphome::FixedVector<const char *> wifi_scan_options(const char *manual) {
  static std::vector<std::string> storage;
  storage.clear();
  for (const auto &r : esphome::wifi::global_wifi_component->get_scan_result()) {
    auto ref = r.get_ssid();
    std::string ssid(ref.c_str(), ref.size());
    // The fonts only carry printable ASCII, anything else draws as a blank box.
    ssid.erase(std::remove_if(ssid.begin(), ssid.end(),
                              [](char c) { return c < 32 || c > 126; }),
               ssid.end());
    if (ssid.empty())                   // hidden network, or nothing printable
      continue;
    if (std::find(storage.begin(), storage.end(), ssid) != storage.end())
      continue;                         // same SSID on 2.4 and 5 GHz
    storage.push_back(ssid);
    if (storage.size() == 12)           // a longer list is not worth scrolling
      break;
  }
  storage.emplace_back(manual);
  esphome::wifi::global_wifi_component->set_keep_scan_results(false);

  esphome::FixedVector<const char *> out;
  out.init(storage.size());
  for (const auto &s : storage)
    out.push_back(s.c_str());
  return out;
}

// ---- skins ---------------------------------------------------------------
//
// One palette per skin, picked by the "Skin" select. Only the main page is
// themed: background, the two big values, the clock, the dim captions, and the
// three CO2 threshold colours (the threshold logic in refresh() reads them from
// here, so a skin cannot end up fighting the air-quality colours).
struct CydSkin {
  uint32_t bg, fg, temp, hum, dim, co2_good, co2_warn, co2_bad;
};

static const CydSkin CYD_SKINS[] = {
  // Contrast - the default: pure white values on near-black, most legible.
  {0x0E1116, 0xFFFFFF, 0xFFFFFF, 0xFFFFFF, 0x8B98A5, 0x4ADE80, 0xFBBF24, 0xF87171},
  // Night - amber on true black, no blue light in an evening living room.
  {0x000000, 0xE8A33D, 0xE8A33D, 0xE8A33D, 0x7A6034, 0x9BBF6A, 0xD9A441, 0xD97757},
  // Day - inverted, for a bright room where a dark panel just mirrors it.
  {0xF2F4F7, 0x0E1116, 0x0E1116, 0x0E1116, 0x54606E, 0x1F7A3D, 0x8A5A00, 0xB3261E},
  // Colour - temperature warm, humidity cool, readable apart at a glance.
  {0x0E1116, 0xF2F4F7, 0xFB923C, 0x38BDF8, 0x8B98A5, 0x4ADE80, 0xFBBF24, 0xF87171},
  // Warm night - like the NoPattern Warm night HA theme: warm off-white on graphite, amber temperature, pink for bad air.
  {0x0E0F14, 0xF2F0EC, 0xFFB547, 0xF2F0EC, 0x9A9890, 0x7FD49A, 0xFFB547, 0xFF2E97},
  // NoPattern - HA's NoPattern Aurora (darker than HA's #04061A: this panel lifts dark colours into bright blue): night blue, aurora orange temperature, cyan humidity, pink for bad air.
  {0x010208, 0xF3F1FF, 0xFF8A3D, 0x2BE4FF, 0xA9A7CC, 0x5EEAD4, 0xFFB547, 0xFF2E97},
};

inline const CydSkin &cyd_skin(int i) {
  const int n = (int) (sizeof(CYD_SKINS) / sizeof(CYD_SKINS[0]));
  return CYD_SKINS[(i < 0 || i >= n) ? 0 : i];   // out of range falls back to Contrast
}

// The "look" on top of the palette: cards behind the values, a glow fading down
// from the top of the page, and the two buttons. The first four skins are flat
// (invisible cards, the original dark buttons, no glow); Warm night and NoPattern
// copy the HA themes: framed cards, a luminous bar + halo on a lit button, and
// for NoPattern the full-gradient lit tile of Aurora.
struct CydBtn {
  uint32_t bg, bg2, line, text;      // lit state: gradient bg -> bg2, border, state text
};
struct CydLook {
  uint32_t top;                      // page gradient: top colour, fading into skin.bg
  uint32_t card, card_line;          // value cards
  uint32_t btn, btn_line;            // buttons, off
  CydBtn heat, cool;                 // fireplace / AC, on
  uint8_t glow;                      // halo width on a lit button, 0 = none
};

inline CydLook cyd_look(int i) {
  if (i == 4)   // Warm night
    return {0x4A3416, 0x18191F, 0x2A2B32, 0x18191F, 0x2A2B32,
            {0x33261A, 0x1E1913, 0xFFB547, 0xFFB547},
            {0x132A33, 0x111A1F, 0x2BE4FF, 0x2BE4FF}, 18};
  if (i == 5)   // NoPattern = NoPattern Aurora
    return {0x1A0A3A, 0x070816, 0x1A1C3A, 0x070816, 0x1A1C3A,
            {0xFF2E97, 0xFF8A3D, 0xFF7AC0, 0xFFFFFF},
            {0x8B3DFF, 0x2BE4FF, 0x7FE9FF, 0xFFFFFF}, 20};
  const uint32_t bg = cyd_skin(i).bg;
  return {bg, bg, bg, 0x1B2028, 0x2E3846,
          {0x7C3A12, 0x7C3A12, 0xF97316, 0xFDBA74},
          {0x0E4A5A, 0x0E4A5A, 0x22D3EE, 0x67E8F9}, 0};
}
