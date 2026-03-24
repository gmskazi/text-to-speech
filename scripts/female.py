import asyncio
import edge_tts

text = """きょねん わたしは かぞくと おおさかに いきました。
電車で いきました。
おおさかで ラーメンを たべました。
おみやげを かいました。
おてらを みました。
とても たのしかったです。
らいねんは おきなわに いきたいです。"""

voice = "ja-JP-NanamiNeural"  # female
output_file = "osaka_story.mp3"


async def main():
    communicate = edge_tts.Communicate(text=text, voice=voice, rate="-20%")
    await communicate.save(output_file)
    print(f"Created {output_file}")


asyncio.run(main())
