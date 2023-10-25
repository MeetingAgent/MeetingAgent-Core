# Voice Cloning Pipeline for custom Text to Speech

## Paragraph to Read for Audio Recording

Upload a .wav audio sample of you reading the below text to the voice_cloning/audio_samples/ directory.

`Once upon a vibrant morning in early spring, Xavier, a keen young botanist from Quebec, embarked on a quaint journey across the knolls and dales of Yellowstone. His zest for flora led him to observe the exquisite orchids blooming amidst the zephyrs. He jotted down notes in a neat, meticulous hand, capturing the essence of each observation. The juxtaposition of junipers and jack pines painted a picturesque panorama, a kaleidoscope of greens under the azure sky. He often hummed a melody that resonated with the serenity of nature, evoking a symphony that harmonized with the rustle of leaves and chirping of birds. Amidst the verdant foliage, Xavier unearthed a rare, vermilion flower, its fragrance wafting gently through the tranquil vale. His journey encapsulated a myriad of experiences, from the euphony of dawn to the velvety silence of dusk, each moment etching indelible impressions upon his soul. The wilderness echoed with whispers of wonder, enunciating the eternal enchantment of nature's tapestry.`

## Model Specifics

On first launch, especially if you do not have the model installed locally, this will take some time.

It is recommended that you have a GPU for faster inference using CUDA, however, this is not necessary. With CPU inference, the model may take several orders of magnitude worth of time more than a GPU will.

Run `get_all_models.py` to get all supported models by TTS
