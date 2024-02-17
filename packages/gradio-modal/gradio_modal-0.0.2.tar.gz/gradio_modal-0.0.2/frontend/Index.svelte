<script lang="ts">
	import { Block } from "@gradio/atoms";
	import Column from "@gradio/column";
	import { Gradio } from "@gradio/utils";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = false;
	export let allow_user_close = true;
	export let gradio: Gradio<{
		blur: never;
	}>;

	let element: HTMLElement | null = null;
	const close = () => {
		visible = false;
		gradio.dispatch("blur");
	};

	document.addEventListener("keydown", (evt: KeyboardEvent) => {
		if (allow_user_close && evt.key === "Escape") {
			close();
		}
	});
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
	class="modal {elem_classes.join(' ')}"
	bind:this={element}
	class:hide={!visible}
	id={elem_id}
	on:click={(evt) => {
		if (allow_user_close && evt.target === element) {
			close();
		}
	}}
>
	<div class="modal-container">
		<Block height="100%">
			{#if allow_user_close}
				<div class="close" on:click={close}>
					<svg
						width="10"
						height="10"
						viewBox="0 0 10 10"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M1 1L9 9"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
						<path
							d="M9 1L1 9"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</div>
			{/if}
			<Column>
				<slot />
			</Column>
		</Block>
	</div>
</div>

<style>
	@media (min-width: 640px) {
		.modal-container {
			max-width: 640px;
		}
	}

	@media (min-width: 768px) {
		.modal-container {
			max-width: 768px;
		}
	}

	@media (min-width: 1024px) {
		.modal-container {
			max-width: 1024px;
		}
	}

	@media (min-width: 1280px) {
		.modal-container {
			max-width: 1280px;
		}
	}

	@media (min-width: 1536px) {
		.modal-container {
			max-width: 1536px;
		}
	}

	.modal {
		position: fixed; /* Stay in place */
		z-index: 100; /* Sit on top */
		left: 0;
		top: 0;
		width: 100%; /* Full width */
		height: 100%; /* Full height */
		z-index: 100;
		background-color: rgb(0, 0, 0); /* Fallback color */
		background-color: rgba(0, 0, 0, 0.4); /* Black w/ opacity */
		backdrop-filter: blur(4px);
	}
	.modal-container {
		padding: 0 var(--size-8);
		margin: var(--size-8) auto;
		max-height: calc(100% - var(--size-8));
		overflow-y: hidden;
	}
	.close {
		display: flex;
		position: absolute;
		top: var(--block-label-margin);
		right: var(--block-label-margin);
		align-items: center;
		box-shadow: var(--shadow-drop);
		border: 1px solid var(--border-color-primary);
		border-top: none;
		border-right: none;
		border-radius: var(--block-label-right-radius);
		background: var(--block-label-background-fill);
		padding: 6px;
		height: 24px;
		overflow: hidden;
		color: var(--block-label-text-color);
		font: var(--font);
		font-size: var(--button-small-text-size);
		cursor: pointer;
	}

	.hide {
		display: none;
	}
</style>
