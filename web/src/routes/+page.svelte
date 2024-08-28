<script>
	export let data;
	import { Alert } from 'flowbite-svelte';
	import VoicesTable from '$lib/components/VoicesTable.svelte';
</script>

<h1>Gen Podcast</h1>

<main>
	<div class="p-8">
		<Alert>
			<span class="font-medium">Info alert!</span>
			Change a few things up and try submitting again.
		</Alert>
	</div>
	<VoicesTable voicesData={data.voices} />
	<pre>
	{JSON.stringify(data, null, 2)}
</pre>
</main>
