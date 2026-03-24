import asyncio
import edge_tts

text = """すみません。きっぷうりばは どこですか。
きっぷうりばは あそこです。
コンビニの となりです。
まっすぐ いってください。
ひだりに まがってください。
きっぷを かってください。
それから ホームに いってください。"""

voice = "ja-JP-NanamiNeural"  # female
output_file = "female2.mp3"


async def main():
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="-20%")
    await communicate.save(output_file)
    print(f"Created {output_file}")


asyncio.run(main())
