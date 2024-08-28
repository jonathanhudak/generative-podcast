// New reusable function for GET requests
async function fetchData(path: string) {
	const response = await fetch(`http://localhost:5432${path}`);
	const data = await response.json();
	return data;
}

/** @type {import('./$types').PageServerLoad} */
export async function load() {
	return {
		...(await fetchData('/podcasts')),
		...(await fetchData('/voices')),
		...(await fetchData('/prompts')),
		...(await fetchData('/scripts'))
	};
}
