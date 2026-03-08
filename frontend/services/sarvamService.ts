import axios from 'axios';

// Use EXPO_PUBLIC_ prefix to make the variable available in the app
const SARVAM_API_KEY = process.env.EXPO_PUBLIC_SARVAM_API_KEY;
const SARVAM_STT_URL = 'https://api.sarvam.ai/speech-to-text';

export type SarvamSTTResponse = {
    transcript: string;
    language_code: string;
    confidence: number;
};

export const transcribeAudio = async (audioUri: string): Promise<SarvamSTTResponse | null> => {
    console.log('Transcribing audio from URI:', audioUri);
    if (!SARVAM_API_KEY) {
        console.error('CRITICAL: EXPO_PUBLIC_SARVAM_API_KEY is undefined. Check your .env file and restart Expo.');
        return null;
    }
    console.log('API Key present (length):', SARVAM_API_KEY.length);

    try {
        const formData = new FormData();

        // Prepare the audio file for the form data
        // In React Native/Expo, we need to provide name and type
        const filename = audioUri.split('/').pop() || 'recording.m4a';

        // @ts-ignore - FormData expects a specific structure for files in RN
        formData.append('file', {
            uri: audioUri,
            name: filename,
            type: 'audio/x-m4a',
        });

        // Optional: You can specify the language if you know it, 
        // or let Sarvam attempt auto-detection if the model supports it.
        // formData.append('language_code', 'hi-IN'); 

        formData.append('model', 'saaras:v3');

        const response = await axios.post(SARVAM_STT_URL, formData, {
            headers: {
                'api-subscription-key': SARVAM_API_KEY,
                'Content-Type': 'multipart/form-data',
            },
        });

        console.log('Sarvam STT response:', response.data);
        return response.data;
    } catch (error: any) {
        if (axios.isAxiosError(error)) {
            console.error('Sarvam STT Error:', error.response?.data || error.message);
        } else {
            console.error('Sarvam STT Unknown Error:', error);
        }
        return null;
    }
};
