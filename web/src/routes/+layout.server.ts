import type { Voice } from '$lib/types/Voices';
import type { PodcastResponse, PromptResponse, ScriptResponse } from '$lib/types/api';

// New reusable function for GET requests
async function fetchData<T>(path: string): Promise<T> {
	const response = await fetch(`http://localhost:5432${path}`);
	const data = await response.json();
	return data;
}

/** @type {import('./$types').PageServerLoad} */
export async function load() {
	return {
		...(await fetchData<PodcastResponse>('/podcasts')),
		...(await fetchData<VoiceResponse>('/voices')),
		...(await fetchData<PromptResponse>('/prompts')),
		...(await fetchData<ScriptResponse>('/scripts'))
	};
}
