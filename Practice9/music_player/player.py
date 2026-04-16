import os
import time
from pathlib import Path

import pygame

SUPPORTED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".ogg",
    ".flac",
    ".m4a",
    ".aac",
    ".opus",
    ".it",
    ".xm",
    ".mod",
}

VLC_IMPORT_ERROR = None

# Add common VLC install folders to PATH before importing python-vlc.
if os.name == "nt":
    candidate_dirs = [
        Path("C:/Program Files/VideoLAN/VLC"),
        Path("C:/Program Files (x86)/VideoLAN/VLC"),
    ]
    for folder in candidate_dirs:
        if folder.exists():
            os.environ["PATH"] = str(folder) + os.pathsep + os.environ.get("PATH", "")
            plugins_dir = folder / "plugins"
            if plugins_dir.exists():
                os.environ.setdefault("VLC_PLUGIN_PATH", str(plugins_dir))

            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(str(folder))
                except Exception:
                    pass
            break

try:
    import vlc
except Exception as error:
    vlc = None
    VLC_IMPORT_ERROR = error

try:
    from mutagen import File as MutagenFile

    HAS_MUTAGEN = True
except Exception:
    HAS_MUTAGEN = False


class MusicPlayer:
    def __init__(self):
        if vlc is None:
            raise RuntimeError(
                "VLC backend is not available. Install python-vlc and VLC Media Player. "
                f"Import error: {VLC_IMPORT_ERROR}"
            )

        self.base_dir = Path(__file__).resolve().parent
        self.music_dir = self.base_dir / "music"
        self.unsupported_tracks = []
        self.playlist = self.load_playlist()
        self.current_index = 0

        self.status = "Stopped"
        self.is_playing = False
        self.waiting_for_start = False
        self.last_play_try_time = 0.0

        self.track_lengths = {}

        try:
            self.vlc_instance = vlc.Instance("--quiet")
            self.media_player = self.vlc_instance.media_player_new()
        except Exception as error:
            raise RuntimeError(
                "Could not start VLC backend. Please install VLC Media Player."
            ) from error

        self.preload_track_lengths()

    def load_playlist(self):
        if not self.music_dir.exists():
            return []

        tracks = []
        for path in sorted(self.music_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
                tracks.append(path)
        return tracks

    def get_track_length(self, track_path):
        if HAS_MUTAGEN:
            try:
                media_info = MutagenFile(str(track_path))
                if media_info and getattr(media_info, "info", None) and hasattr(media_info.info, "length"):
                    return float(media_info.info.length)
            except Exception:
                pass
        return 0.0

    def preload_track_lengths(self):
        for track_path in self.playlist:
            self.track_lengths[track_path] = self.get_track_length(track_path)

    def get_current_track(self):
        if not self.playlist:
            return None
        return self.playlist[self.current_index]

    def mark_track_unsupported_and_skip(self, track_name):
        if track_name not in self.unsupported_tracks:
            self.unsupported_tracks.append(track_name)

        # remove current problematic track
        if self.playlist:
            self.playlist.pop(self.current_index)
            if self.current_index >= len(self.playlist) and self.playlist:
                self.current_index = 0

    def play_current_track(self):
        track = self.get_current_track()
        if track is None:
            self.status = "No tracks found in music folder."
            self.is_playing = False
            self.waiting_for_start = False
            return

        try:
            media = self.vlc_instance.media_new(str(track))
            self.media_player.set_media(media)
            play_result = self.media_player.play()
            if play_result == -1:
                raise RuntimeError("VLC failed to start playback.")
        except Exception:
            bad_track = track.name
            self.mark_track_unsupported_and_skip(bad_track)

            if not self.playlist:
                self.status = f"Track not supported: {bad_track}. No playable tracks left."
                self.is_playing = False
                self.waiting_for_start = False
                return

            self.status = f"Skipped unsupported track: {bad_track}"
            self.play_current_track()
            return

        # make sure volume/mute state is audible
        self.media_player.audio_set_mute(False)
        self.media_player.audio_set_volume(100)

        self.is_playing = True
        self.waiting_for_start = True
        self.last_play_try_time = time.monotonic()
        self.status = "Starting..."

    def stop_track(self):
        self.media_player.stop()
        self.is_playing = False
        self.waiting_for_start = False
        self.status = "Stopped"

    def next_track(self):
        if not self.playlist:
            self.status = "No tracks found in music folder."
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current_track()

    def previous_track(self):
        if not self.playlist:
            self.status = "No tracks found in music folder."
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current_track()

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_p:
            self.play_current_track()
        elif event.key == pygame.K_s:
            self.stop_track()
        elif event.key == pygame.K_n:
            self.next_track()
        elif event.key == pygame.K_b:
            self.previous_track()
        elif event.key == pygame.K_q:
            return "quit"

        return None

    def update(self):
        if not self.is_playing:
            return

        state = self.media_player.get_state()

        # wait a bit for VLC to transition into Playing
        if self.waiting_for_start:
            if state in (vlc.State.Playing, vlc.State.Paused):
                self.waiting_for_start = False
                self.status = "Playing"
                return

            if state == vlc.State.Error:
                current = self.get_current_track()
                if current is not None:
                    self.mark_track_unsupported_and_skip(current.name)
                self.waiting_for_start = False
                if not self.playlist:
                    self.status = "Track failed to start. No playable tracks left."
                    self.is_playing = False
                else:
                    self.status = "Track failed to start. Skipping..."
                    self.play_current_track()
                return

            if time.monotonic() - self.last_play_try_time > 5:
                current = self.get_current_track()
                if current is not None:
                    self.mark_track_unsupported_and_skip(current.name)
                self.waiting_for_start = False
                if not self.playlist:
                    self.status = "Track did not start. No playable tracks left."
                    self.is_playing = False
                else:
                    self.status = "Track did not start in time. Skipping..."
                    self.play_current_track()
                return

        if state == vlc.State.Ended:
            self.next_track()
        elif state == vlc.State.Error:
            current = self.get_current_track()
            if current is not None:
                self.mark_track_unsupported_and_skip(current.name)
            if not self.playlist:
                self.status = "Playback error. No playable tracks left."
                self.is_playing = False
            else:
                self.status = "Playback error. Skipping track..."
                self.play_current_track()

    def format_seconds(self, seconds):
        total = max(0, int(seconds))
        minutes = total // 60
        sec = total % 60
        return f"{minutes:02d}:{sec:02d}"

    def get_progress_text(self):
        track = self.get_current_track()
        if track is None:
            return "--:-- / --:--"

        total_seconds = self.track_lengths.get(track, 0)
        current_ms = self.media_player.get_time()

        if current_ms < 0 or not self.is_playing or self.waiting_for_start:
            current_seconds = 0
        else:
            current_seconds = current_ms / 1000.0

        if total_seconds > 0 and current_seconds > total_seconds:
            current_seconds = total_seconds

        return f"{self.format_seconds(current_seconds)} / {self.format_seconds(total_seconds)}"

    def draw_ui(self, screen, title_font, text_font):
        screen.fill((235, 245, 255))

        title = title_font.render("Music Player", True, (15, 15, 15))
        controls = text_font.render("P=Play  S=Stop  N=Next  B=Back  Q=Quit", True, (30, 30, 30))
        status = text_font.render(f"Status: {self.status}", True, (20, 20, 20))

        track = self.get_current_track()
        if track is None:
            track_name = "No tracks loaded"
        else:
            track_name = track.name

        track_text = text_font.render(f"Current Track: {track_name}", True, (20, 20, 20))
        progress_text = text_font.render(f"Progress: {self.get_progress_text()}", True, (20, 20, 20))

        screen.blit(title, (30, 30))
        screen.blit(controls, (30, 100))
        screen.blit(status, (30, 170))
        screen.blit(track_text, (30, 240))
        screen.blit(progress_text, (30, 310))

        info = text_font.render("Formats: wav, mp3, ogg, flac, m4a, aac, opus...", True, (30, 30, 30))
        screen.blit(info, (30, 390))

        if self.unsupported_tracks:
            unsupported_title = text_font.render("Skipped unsupported files:", True, (180, 30, 30))
            screen.blit(unsupported_title, (30, 430))

            names_preview = ", ".join(self.unsupported_tracks[:2])
            if len(self.unsupported_tracks) > 2:
                names_preview += f" ... (+{len(self.unsupported_tracks) - 2} more)"

            unsupported_names = text_font.render(names_preview, True, (120, 20, 20))
            screen.blit(unsupported_names, (30, 465))

    def close(self):
        try:
            self.media_player.stop()
        except Exception:
            pass