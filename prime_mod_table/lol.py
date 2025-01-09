import pyaudio
import numpy as np
import curses
import math


def generate_sine_wave(frequency, length, rate):
    """Generate a synthetic sine wave for testing."""
    t = np.linspace(0, length, int(rate * length), endpoint=False)
    return (0.5 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)


def audio_visualizer(stdscr):
    # Configure curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # Initialize color pairs for dynamic bars
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    # Audio stream settings
    CHUNK = 1024
    RATE = 44100
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    NOISE_THRESHOLD = 500  # Threshold to treat low values as silence

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
    except Exception as e:
        print(f"Error initializing audio stream: {e}")
        stream = None

    try:
        while True:
            # Read audio data or simulate if no stream
            if stream:
                data = np.frombuffer(
                    stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16
                )
            else:
                data = generate_sine_wave(
                    440, CHUNK / RATE, RATE
                )  # Simulated sine wave

            # Process audio data
            data = np.abs(data)  # Absolute values for amplitude
            num_bars = curses.COLS // 2
            chunk_size = len(data) // num_bars
            bars = [
                data[i * chunk_size : (i + 1) * chunk_size].mean()
                for i in range(num_bars)
            ]

            # Normalize and apply noise threshold
            if max(bars) < NOISE_THRESHOLD:
                bars = [0] * len(bars)
            else:
                bars = np.interp(bars, (0, max(bars)), (0, curses.LINES - 1))

            # Clear screen and render bars
            stdscr.clear()
            for i, bar_height in enumerate(bars):
                # Assign color based on height
                color_pair = (
                    1
                    if bar_height > curses.LINES * 0.7
                    else 2 if bar_height > curses.LINES * 0.4 else 3
                )
                for j in range(int(bar_height)):
                    stdscr.addstr(
                        curses.LINES - 1 - j, i * 2, "█", curses.color_pair(color_pair)
                    )

            stdscr.refresh()

            # Quit on 'q'
            key = stdscr.getch()
            if key == ord("q"):
                break
    finally:
        # Clean up
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()


if __name__ == "__main__":
    curses.wrapper(audio_visualizer)
