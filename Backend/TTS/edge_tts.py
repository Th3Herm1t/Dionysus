import os
import edge_tts
import logging
import asyncio

# Initialize logging
logger = logging.getLogger(__name__)

class EdgeTTSClient:
    def __init__(self, voice="en-US-JennyNeural"):
        self.voice = voice

    async def synthesize_post(self, text, folder_path, rate="100%"):
        """
        Synthesizes speech from the provided text and saves it as an audio file.
        
        :param text: The text to synthesize.
        :param folder_path: The path where the audio file will be saved.
        :param rate: The speech rate for synthesis (default is "100%").
        :return: Paths to the saved audio and VTT files.
        """
        # Validate the rate
        rate = self.validate_rate(rate)
        
        # Create output file paths
        audio_path = os.path.join(folder_path, 'narration.mp3')
        vtt_path = os.path.join(folder_path, 'narration.vtt')

        # Initialize the TTS communicate object
        communicate = edge_tts.Communicate(text, voice=self.voice)

        try:
            # Save the audio
            await communicate.save(audio_path)
            logger.info(f"Synthesized audio saved at: {audio_path}")

            # Generate VTT subtitles
            await self.generate_vtt(text, vtt_path)

            return audio_path, vtt_path
        except Exception as e:
            logger.error(f"Error in synthesizing speech: {e}")
            return None, None

    async def generate_vtt(self, text, vtt_path):
        """
        Generates VTT subtitles from the provided text.
        
        :param text: The text to synthesize for VTT.
        :param vtt_path: The path where the VTT file will be saved.
        """
        # Initialize the TTS communicate object for VTT generation
        communicate = edge_tts.Communicate(text, voice=self.voice)
        submaker = edge_tts.SubMaker()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

        with open(vtt_path, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())
        logger.info(f"Subtitles saved at: {vtt_path}")

    @staticmethod
    def validate_rate(rate):
        """
        Validates the rate input to ensure it's in the correct format.
        
        :param rate: The rate string to validate.
        :return: A valid rate string.
        """
        try:
            if not rate.endswith('%') or int(rate[:-1]) <= 0:
                raise ValueError("Invalid rate provided")
            return rate
        except ValueError:
            logger.warning("Invalid rate format. Defaulting to '100%'.")
            return "100%"  # Default to a valid rate if the input is invalid

# Example of usage
if __name__ == "__main__":
    async def main():
        tts_client = EdgeTTSClient()
        text = "Hello, this is a test of the edge TTS synthesis."
        folder_path = "./output"  # Ensure this folder exists
        os.makedirs(folder_path, exist_ok=True)
        await tts_client.synthesize_post(text, folder_path)

    asyncio.run(main())