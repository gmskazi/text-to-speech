import asyncio
import edge_tts
import subprocess
import os

lines = [
    ("A", "すみません。きっぷうりばは どこですか。"),
    (
        "B",
        """きっぷうりばは あそこです。
コンビニの となりです。
まっすぐ いってください。
ひだりに まがってください。
きっぷを かってください。
それから ホームに いってください。""",
    ),
]

voices = {"A": "ja-JP-NanamiNeural", "B": "ja-JP-KeitaNeural"}

output_file = "roleplay_final.mp3"
list_file = "concat.txt"
temp_files = []


async def generate():
    for i, (speaker, text) in enumerate(lines):
        voice = voices[speaker]
        filename = f"line_{i}.mp3"
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="-20%")
        await communicate.save(filename)
        temp_files.append(filename)


async def main():
    print("Generating voices...")
    await generate()

    with open(list_file, "w", encoding="utf-8") as f:
        for name in temp_files:
            f.write(f"file '{name}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file,
            "-c",
            "copy",
            output_file,
        ],
        check=True,
    )

    for name in temp_files:
        if os.path.exists(name):
            os.remove(name)
    if os.path.exists(list_file):
        os.remove(list_file)

    print(f"Created {output_file}")


asyncio.run(main())
