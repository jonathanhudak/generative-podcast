import type { Voice } from '$lib/types/Voices';

// New reusable function for GET requests
async function fetchData<T>(path: string): Promise<T> {
	const response = await fetch(`http://localhost:5432${path}`);
	const data = await response.json();
	return data;
}

/** @type {import('./$types').PageServerLoad} */
export async function load() {
	return {
		...(await fetchData<{ podcasts: { id: string }[] }>('/podcasts')),
		...(await fetchData<{ voices: Voice[] }>('/voices')),
		...(await fetchData<{ prompts: { id: string }[] }>('/prompts')),
		...(await fetchData<{ scripts: { id: string }[] }>('/scripts'))
	};
}
