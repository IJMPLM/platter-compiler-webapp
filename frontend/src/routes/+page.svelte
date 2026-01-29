<script lang="ts">
	// Restored functionality: bind editor, call backend, populate lexer table, and show terminal messages
	import {
		check,
		copy,
		copy1,
		darkmode,
		darkmode1,
		darkBg,
		lightBg,
		editor,
		editor1,
		errorIcon,
		errors,
		errors1,
		favicon,
		lightmode,
		logo,
		newFile,
		newFile1,
		openFile,
		openFile1,
		refresh,
		refresh1,
		saveFile,
		saveFile1,
		synSemLexIcon,
		synSemLexIcon1,
		table,
		warning
	} from '$lib';

	import { onMount, onDestroy } from 'svelte';
	import {
		loadScript,
		loadCSS,
		readFileAsText,
		saveContent,
		copyToClipboard
	} from '$lib/utils/browser';

	let theme: 'dark' | 'light' = 'dark';
	let activeTab: 'lexical' | 'syntax' | 'semantic' = 'lexical';

	let codeInput = `piece of x = 42;
sip of y = 3.67;
chars[] of names = ["Hello Platter", "Raph", "Jieco"];

prepare sip of sips() { check(topiece(y) > x) { serve x;} instead {serve y;} }

prepare piece of pieces() {
	serve x;
}

start() {
	piece of z = topiece(topiece(sips()) + pieces());
	serve z;
}`;

	type Token = { type: string; value: string; line: number; col: number };
	const lexerRows: Array<{ lexeme: string; token: string }> = [];
	let tokens: Token[] = [];
	let isAnalyzing = false;

	// CodeMirror integration
	let textareaEl: HTMLTextAreaElement | null = null;
	let cmInstance: any = null;
	let errorMarkers: any[] = []; // Track CodeMirror text markers for error highlighting

	// file input for opening .platter files
	let fileInputEl: HTMLInputElement;

	function openFileDialog() {
		fileInputEl?.click();
	}

	async function handleFileInput() {
		const f = fileInputEl?.files?.[0];
		if (!f) return;
		if (!f.name || !f.name.toLowerCase().endsWith('.platter')) {
			setTerminalError('Please select a .platter file');
			fileInputEl.value = '';
			return;
		}
		try {
			const text = await readFileAsText(f);
			codeInput = text;
			if (cmInstance && typeof cmInstance.setValue === 'function') {
				cmInstance.setValue(text);
			}
			setTerminalOk(`Opened ${f.name}`);
		} catch (err) {
			setTerminalError('Failed to read file');
		} finally {
			// reset input so the same file can be selected again
			fileInputEl.value = '';
		}
	}

	// Save current editor content as a .platter file. Uses the File System Access API when available,
	// otherwise falls back to a download via an anchor element.
	async function saveFileDialog() {
		const content =
			cmInstance && typeof cmInstance.getValue === 'function' ? cmInstance.getValue() : codeInput;
		try {
			const msg = await saveContent(content, 'program.platter');
			setTerminalOk(msg);
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Save cancelled or failed';
			setTerminalError(`Save failed: ${msg}`);
		}
	}

	function definePlatterMode() {
		const CM = (window as any).CodeMirror;
		if (!CM) return;

		// Define keyword sets
		const keywords = {
			conditional: ['alt', 'check', 'instead'],
			logical: ['and', 'or', 'not'],
			loop: ['order', 'repeat'],
			control: ['pass', 'menu', 'choice', 'stop', 'next', 'usual'],
			method: ['append', 'bill', 'copy', 'cut', 'fact', 'matches', 'size', 'sort', 'sqrt', 'tochars', 'topiece', 'take', 'tosip', 'rand', 'pow', 'remove', 'reverse', 'search'],
			type: ['chars', 'flag', 'piece', 'sip'],
			boolean: ['down', 'up'],
			function: ['prepare', 'start'],
			return: ['serve', 'of'],
			struct: ['table']
		};

		// Create a set for quick lookup
		const keywordMap = new Map<string, string>();
		Object.entries(keywords).forEach(([category, words]) => {
			words.forEach(word => keywordMap.set(word, category));
		});

		CM.defineMode('platter', function() {
			return {
				startState: function() {
					return { inString: false, stringChar: '' };
				},
				token: function(stream: any, state: any) {
					// Skip whitespace
					if (stream.eatSpace()) return null;

					// Handle strings
					if (state.inString) {
						while (!stream.eol()) {
							if (stream.next() === state.stringChar) {
								state.inString = false;
								break;
							}
							// Check for escape sequences within strings
							if (stream.current() === '\\') {
								const nextChar = stream.peek();
								if (nextChar === 'n' || nextChar === 't') {
									return 'escape-sequence';
								}
							}
						}
						return 'string';
					}

					// Start a string
					if (stream.eat('"')) {
						state.inString = true;
						state.stringChar = '"';
						return 'string';
					}

					// Handle escape sequences
					if (stream.eat('\\')) {
						if (stream.eat('n') || stream.eat('t')) {
							return 'escape-sequence';
						}
						return 'escape-sequence';
					}

					// Handle numbers
					if (stream.match(/^\d+(\.\d+)?/)) {
						return 'number';
					}

					// Handle identifiers and keywords
					if (stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*/)) {
						const word = stream.current();
						const category = keywordMap.get(word);
						if (category) {
							return `keyword-${category}`;
						}
						return 'variable';
					}

					// Handle compound operators (must be before single-char operators)
					if (stream.match(/^(==|!=|<=|>=|\+=|-=|\*=|\/=|%=)/)) {
						return 'operator-compound';
					}

					// Handle single-char operators
					if (stream.match(/^[=\+\-\*\/%<>]/)) {
						return 'operator-arithmetic';
					}

					// Handle delimiters
					if (stream.match(/^[{}\[\](),:;]/)) {
						return 'delimiter';
					}

					// Handle comments
					if (stream.eat('#')) {
						stream.skipToEnd();
						return 'comment';
					}

					// Skip any other character
					stream.next();
					return null;
				}
			};
		});
	}

	onMount(async () => {
		try {
			// load CodeMirror assets from CDN (lightweight integration)
			await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css');
			// optional: a theme could be loaded here, but our overrides will ensure transparency
			await loadScript(
				'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js'
			);
			if (textareaEl && (window as any).CodeMirror) {
				const CM = (window as any).CodeMirror;
				
				// Define the Platter mode
				definePlatterMode();
				
				cmInstance = CM.fromTextArea(textareaEl, {
					lineNumbers: true,
					// enable soft-wrapping so long lines flow to the next visual line
					lineWrapping: true,
					viewportMargin: Infinity,
					mode: 'platter'
				});
				cmInstance.setSize('100%', '100%');
				cmInstance.on('change', () => {
					codeInput = cmInstance.getValue();
				});
			}
		} catch (err) {
			console.warn('Failed to load CodeMirror from CDN:', err);
		}
	});

	onDestroy(() => {
		if (cmInstance && typeof cmInstance.toTextArea === 'function') {
			cmInstance.toTextArea();
			cmInstance = null;
		}
	});

	// Terminal messages
	type TermMsg = { icon: string; text: string };
	// default to empty terminal (no messages) so termMessages.length === 0
	let termMessages: TermMsg[] = [];

	// Compute error count: treat messages that start with "Lexical OK" as non-errors (count as zero)
	$: errorCount = termMessages.filter(
		(m) =>
			!(
				typeof m.text === 'string' &&
				(m.text.startsWith('Lexical OK') || m.text.startsWith('No Syntax Error'))
			)
	).length;

	function setTerminalOk(message = 'No Error') {
		termMessages = [{ icon: check, text: message }];
	}
	function setTerminalError(message: string) {
		termMessages = [{ icon: errorIcon, text: message }];
	}
	function clearTerminal() {
		termMessages = [];
	}

	function clearErrorMarkers() {
		if (cmInstance) {
			errorMarkers.forEach((marker) => marker.clear());
			errorMarkers = [];
		}
	}

	function addErrorMarkers(errors: Token[]) {
		if (!cmInstance) return;
		clearErrorMarkers();
		errors.forEach((error) => {
			const line = error.line - 1; // CodeMirror uses 0-based line numbers
			const col = error.col - 1; // CodeMirror uses 0-based columns
			const valueLength = error.value?.length || 1;
			const marker = cmInstance.markText(
				{ line, ch: col },
				{ line, ch: col + valueLength },
				{ className: 'error-underline' }
			);
			errorMarkers.push(marker);
		});
	}

	function normalizeQuotes(text: string): string {
		// Convert curly quotes to straight quotes using Unicode escape sequences
		// \u201C = left double quotation mark (")
		// \u201D = right double quotation mark (")
		return text.replace(/[\u201C\u201D]/g, '"');
	}

	async function analyzeSemantic() {
		activeTab = 'semantic';
		if (!codeInput) {
			setTerminalError('No code to analyze');
			return;
		}
		isAnalyzing = true;
		clearErrorMarkers();
		clearTerminal();
		codeInput = normalizeQuotes(codeInput);
		if (cmInstance && typeof cmInstance.setValue === 'function') {
			cmInstance.setValue(codeInput);
		}

		try {
			const res = await fetch('http://localhost:8000/analyzeSemantic', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ code: codeInput })
			});
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const data = await res.json();

			if (data.success) {
				clearErrorMarkers();
				// Log AST structure to console
				if (data.ast_string) {
					console.log('=== Abstract Syntax Tree ===');
					console.log(data.ast_string);
					console.log('=== AST Dictionary ===');
					console.log(data.ast);
				}
				// Show success message in terminal
				setTerminalOk(data.message || 'No Semantic Error');
			} else {
				// Handle semantic errors with line/col information
				if (data.error && data.error.line && data.error.col) {
					// Create a token-like object for the error marker
					const errorToken = {
						type: 'Semantic Error',
						value: 'error',
						line: data.error.line,
						col: data.error.col
					};
					addErrorMarkers([errorToken]);
				}
				setTerminalError(data.message || 'Semantic analysis failed');
			}
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Unknown error';
			setTerminalError(`Semantic analysis failed: ${msg}`);
		} finally {
			isAnalyzing = false;
		}
	}

	async function analyzeSyntax() {
		codeInput = normalizeQuotes(codeInput);
		if (cmInstance && typeof cmInstance.setValue === 'function') {
			cmInstance.setValue(codeInput);
		}
		await analyzeLexical();

		if (termMessages.length === 1 && termMessages[0].text.startsWith('Lexical OK')) {
			clearTerminal();

			try {
				const res = await fetch('http://localhost:8000/analyzeSyntax', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ code: codeInput })
				});
				if (!res.ok) throw new Error(`HTTP ${res.status}`);
				const data = await res.json();

				if (data.success) {
					clearErrorMarkers();
					setTerminalOk(data.message || 'Syntax analysis completed successfully');
				} else {
					// Handle syntax errors with line/col information
					if (data.error && data.error.line && data.error.col) {
						// Create a token-like object for the error marker
						const errorToken = {
							type: 'Syntax Error',
							value: 'error',
							line: data.error.line,
							col: data.error.col
						};
						addErrorMarkers([errorToken]);
					}
					setTerminalError(data.message || 'Syntax analysis failed');
				}
			} catch (err) {
				const msg = err instanceof Error ? err.message : 'Unknown error';
				setTerminalError(`Syntax analysis failed: ${msg}`);
			}
		} else if (termMessages.length > 0) {
			termMessages = [
				{ icon: errorIcon, text: 'Syntax analysis not performed due to lexical errors:' },
				...termMessages
			];
		} else {
			setTerminalOk('Syntax analysis not yet implemented');
		}

		activeTab = 'syntax';
	}

	async function analyzeLexical() {
		activeTab = 'lexical';
		if (!codeInput) {
			setTerminalError('Editor is empty');
			return;
		}
		isAnalyzing = true;
		codeInput = normalizeQuotes(codeInput);
		if (cmInstance && typeof cmInstance.setValue === 'function') {
			cmInstance.setValue(codeInput);
		}
		try {
			const res = await fetch('http://localhost:8000/analyzeLexical', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ code: codeInput })
			});
			if (!res.ok) throw new Error(`HTTP ${res.status}`);
			const data = (await res.json()) as { success: boolean; tokens: Token[] };
			// receive tokens and separate unknown/error tokens into the terminal
			const received = data.tokens ?? [];
			// treat tokens with type starting with 'invalid' or 'exceeds' (case-insensitive) as lexical errors
			const invalidTokens = received.filter(
				(t) =>
					typeof t.type === 'string' &&
					(t.type.toLowerCase().startsWith('invalid') || t.type.toLowerCase().startsWith('exceeds'))
			);
			// tokens to show in the lexer table (exclude invalids and exceeds)
			tokens = received.filter(
				(t) =>
					!(
						typeof t.type === 'string' &&
						(t.type.toLowerCase().startsWith('invalid') ||
							t.type.toLowerCase().startsWith('exceeds'))
					)
			);

			// update right table
			lexerRows.length = 0;
			// Group consecutive spaces, newlines, and tabs (but reset count when invalid tokens appear)
			// We need to track position in original received array to detect when errors interrupt whitespace
			const invalidPositions = new Set(invalidTokens.map((t) => `${t.line}:${t.col}:${t.value}`));

			let i = 0;
			let receivedIdx = 0;

			while (i < tokens.length) {
				const t = tokens[i];
				const tokenType = t.type.toLowerCase();

				// Check if this is a space, newline, or tab token
				if (tokenType === 'space' || tokenType === 'newline' || tokenType === 'tab') {
					let count = 1;
					let nextIdx = i + 1;

					// Count consecutive identical tokens, but stop if an invalid token was between them in original stream
					while (nextIdx < tokens.length && tokens[nextIdx].type.toLowerCase() === tokenType) {
						// Check if there's an invalid token between current and next in the original stream
						const currentToken = tokens[i + count - 1];
						const nextToken = tokens[nextIdx];

						// Simple heuristic: if line/col gap suggests something was between them, stop counting
						const hasGap =
							nextToken.line > currentToken.line + 1 ||
							(nextToken.line === currentToken.line && nextToken.col > currentToken.col + 1);

						if (hasGap) {
							// There might be an invalid token between, stop grouping
							break;
						}

						count++;
						nextIdx++;
					}

					// Add a single row with count if more than 1
					const displayToken = count > 1 ? `${t.type} (${count})` : t.type;
					lexerRows.push({ lexeme: t.value ?? '', token: displayToken });
					i += count;
				} else {
					// Regular token, add as-is
					lexerRows.push({ lexeme: t.value ?? '', token: t.type });
					i++;
				}
			}

			if (invalidTokens.length) {
				// Format error messages based on token type
				const combinedErrors: TermMsg[] = [];
				let i = 0;

				while (i < invalidTokens.length) {
					const current = invalidTokens[i];
					let errorText = '';

					if (current.type === 'Invalid Character') {
						// Format: Error at line X col Y - Invalid Character: <character>
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Character: ${current.value}`;
					} else if (current.type === 'Invalid Identifier') {
						// Format: Error at line X col Y - Invalid Lexeme: <RW> cannot be an identifier
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} cannot be an identifier`;
					} else if (current.type === 'Invalid Lexeme') {
						// Format: Error at line X col Y - Invalid Lexeme: <invalid lexeme>
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value}`;
					} else if (current.type.toLowerCase().startsWith('exceeds')) {
						// Determine if it's an identifier or literal based on first character
						const firstChar = current.value?.charAt(0) || '';
						const isIdentifier = /[a-zA-Z_]/.test(firstChar);
						const isLiteral = /[0-9]/.test(firstChar);

						let limitType = '';
						if (isIdentifier) {
							limitType = 'id';
						} else if (isLiteral) {
							limitType = 'piece/sip literal';
						} else {
							limitType = 'value';
						}

						// Format: Error at line X col Y - Invalid Lexeme: <value> exceeds <type> limit
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} exceeds ${limitType} limit`;
					} else {
						// Fallback for any other error types
						errorText = `Error at line ${current.line} col ${current.col} - ${current.type}: ${current.value}`;
					}

					combinedErrors.push({
						icon: errorIcon,
						text: errorText
					});
					i += 1;
				}

				termMessages = combinedErrors;
				// Highlight errors in CodeMirror
				addErrorMarkers(invalidTokens);
				// also set a concise terminal summary
				// keep lexer table OK message minimal
				return;
			}

			clearErrorMarkers();

			setTerminalOk(
				tokens.length ? `Lexical OK • ${tokens.length} token(s)` : 'No tokens produced'
			);
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Unknown error';
			setTerminalError(`Lexical analysis failed: ${msg}`);
		} finally {
			isAnalyzing = false;
		}
	}

	function toggleTheme() {
		theme = theme === 'dark' ? 'light' : 'dark';
	}

	async function handleCopyToClipboard() {
		const content =
			cmInstance && typeof cmInstance.getValue === 'function' ? cmInstance.getValue() : codeInput;
		try {
			await copyToClipboard(content);
			setTerminalOk('Content copied to clipboard');
		} catch (err) {
			setTerminalError('Failed to copy to clipboard');
		}
	}
</script>

<div class="ide" data-theme={theme} style={`--bg-img: url(${theme === 'dark' ? darkBg : lightBg})`}>
	<!-- Top bar -->
	<header class="titlebar">  
		<div class="brand">
			<img class="logo" src={logo} alt="Platter logo" />
			<span class="name">Platter IDE</span>
		</div>
		<div class="win-controls">
			<span class="dot" title="minimize"></span>
			<span class="dot" title="maximize"></span>
			<span class="dot" title="close"></span>
		</div>
	</header>

	<!-- Main grid: left workspace and right sidebar -->
	<div class="grid">
		<!-- LEFT WORKSPACE -->
		<section class="left">
			<!-- Toolbar row -->
			<div class="toolbar">
				<button class="pill {activeTab === 'lexical' ? 'active' : ''}" on:click={analyzeLexical}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Lexical Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}

					<span>Lexical</span>
				</button>
				<!-- syntax and semantic methods to be replacesrd -->
				<button class="pill {activeTab === 'syntax' ? 'active' : ''}" on:click={analyzeSyntax}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Lexical Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}
					<span>Syntax</span>
				</button>
				<button class="pill {activeTab === 'semantic' ? 'active' : ''}" on:click={analyzeSemantic}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Semantic Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}
					<span>Semantic</span>
				</button>

				<div class="spacer"></div>
				<!-- replace icons based on theme -->
				<button
					class="icon-btn"
					title="refresh"
					on:click={() => {
						if (cmInstance) cmInstance.setValue('');
						codeInput = '';
						clearTerminal();
						clearErrorMarkers();
						lexerRows.length = 0;
						tokens = [];
					}}
					>{#if theme === 'dark'}
						<img class="icon" src={refresh} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={refresh1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="copy" on:click={handleCopyToClipboard}
					>{#if theme === 'dark'}
						<img class="icon" src={copy} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={copy1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="Theme" on:click={toggleTheme}>
					{#if theme === 'dark'}
						<img class="icon" src={lightmode} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={darkmode} alt="Light Theme Icon" />
					{/if}
				</button>
			</div>

			<!-- Editor canvas -->
			<div class="panel editor" style={`--editor-img: url(${theme === 'dark' ? editor : editor1})`}>
				<textarea
					class="editor-area"
					bind:this={textareaEl}
					bind:value={codeInput}
					placeholder="Write your Platter code here..."
					spellcheck="false"
				></textarea>
			</div>

			<!-- Terminal panel -->
			<div
				class="panel terminal"
				style={`--terminal-img: url(${theme === 'dark' ? errors : errors1})`}
			>
				<div class="terminal-head">
					<span class="title">Terminal</span>
					<!-- error count (ignore 'Lexical OK' messages) -->

					<div class="counter">
						<span>Errors: {errorCount} </span>
						{#if errorCount > 0}
							<img class="icon" src={warning} alt="warning" />
						{/if}
					</div>
				</div>
				<div class="terminal-body">
					{#each termMessages as e}
						<div class="trow">
							<img class="ticon-img" src={e.icon} alt="" />
							<span class="tmsg">{e.text}</span>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- RIGHT SIDEBAR -->
		<aside class="right">
			<div class="actions">
				<button
					class="btn"
					on:click={() => {
						const newWindow = window.open(window.location.href, '_blank');
						if (newWindow) setTimeout(() => (newWindow.document.body.style.zoom = '80%'), 100);
					}}
				>
					{#if theme === 'dark'}
						<img class="icon" src={newFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={newFile1} alt="Light Theme Icon" />
					{/if} <span>New Tab</span></button
				>
				<button class="btn" type="button" on:click={openFileDialog}>
					{#if theme === 'dark'}
						<img class="icon" src={openFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={openFile1} alt="Light Theme Icon" />
					{/if}
					<span>Open File</span></button
				>
				<!-- hidden file input for opening .platter files -->
				<input
					type="file"
					accept=".platter"
					bind:this={fileInputEl}
					on:change={handleFileInput}
					style="display:none"
				/>
				<button class="btn" type="button" on:click={saveFileDialog}>
					{#if theme === 'dark'}
						<img class="icon" src={saveFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={saveFile1} alt="Light Theme Icon" />
					{/if} <span>Save File</span></button
				>
			</div>

			<div class="panel table" style={`--table-img: url(${table})`}>
				<div class="table-title">Lexer Table</div>
				<div class="table-head">
					<div>Lexeme</div>
					<div>Token</div>
				</div>
				<div class="table-body">
					{#if lexerRows.length === 0}
						<div class="empty">No tokens yet</div>
					{:else}
						{#each lexerRows as row}
							<div class="table-row">
								<div>{row.lexeme}</div>
								<div>{row.token}</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</aside>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
	}

	.ide {
		--bg: #2b2b2f;
		--bg-soft: #2f2f34;
		--ink: #f2f2f2;
		--ink-muted: #c9c9cf;
		--accent: #ffffff;
		--outline: #ffffff;
		--panel: rgba(255, 255, 255, 0.03);
		--shadow: 0 0 0 2px var(--outline) inset;
		min-height: 100dvh;
		/* Use Svelte-provided CSS var for image */
		background-image: var(--bg-img);
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		background-color: #26262a; /* fallback color */
		color: var(--ink);
		font-family: 'Inter', Roboto, sans-serif;
		font-weight: 700; /* Inter bold as default, Roboto as fallback */
	}

	.ide[data-theme='light'] {
		--bg: #f7f7fb;
		--bg-soft: #fff;
		--ink: #1f1f23;
		--ink-muted: #555;
		--accent: #111;
		--outline: #111;
		background-image: var(--bg-img);
	}

	.titlebar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: #77787e;
		color: #fff;
		padding: 8px 12px;
		user-select: none;
	}

	.title {
		font-size: 14px;
		margin-left: 24px;
		margin-bottom: 8px;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 600;
	}
	.logo {
		filter: grayscale(0.1);
		width: 30px;
		height: 30px;
		object-fit: contain;
	}
	.name {
		letter-spacing: 0.2px;
	}
	.win-controls {
		display: flex;
		gap: 8px;
	}
	.dot {
		width: 12px;
		height: 12px;
		border-radius: 999px;
		background: #cfcfd6;
		display: inline-block;
	}

	.grid {
		display: grid;
		width: 100%;
		/* Let the right column grow to take available space */
		grid-template-columns: 1fr minmax(420px, 1fr);
		gap: 16px;
		padding: 16px;
	}

	.toolbar {
		display: flex;
		width: 100%;
		align-items: center;
		gap: 8px;
		background: transparent;
		color: var(--ink);
		border-radius: 8px;
		cursor: pointer;
		margin-right: 8px;
		margin-top: 12px;
	}

	.pill {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 28px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
		margin-right: 8px;
	}
	.pill.active {
		background: rgba(255, 255, 255, 0.08);
	}
	.spacer {
		flex: 1;
	}
	.icon-btn {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
	}

	/* toolbar icon image inside buttons */
	.icon {
		width: 18px;
		height: 18px;
		object-fit: contain;
	}

	.left {
		display: flex;
		flex-direction: column;
		width: 1130px;
	}
	.panel {
		/* background: var(--panel); */
		border-radius: 14px;
		padding: 10px;
		border: 4px solid var(--outline);

		box-shadow: var(--shadow);
	}
	.editor {
		/* use the `editor` SVG asset for background */
		background-image: var(--editor-img);
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
	}
	.editor + .terminal {
		margin-top: 10px;

		border: none;
	}

	.terminal {
		width: 100%;
		background-image: var(--terminal-img);
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
		outline: none;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
		font-size: 18px;
		height: 300px;
	}

	.editor-area {
		width: 95.5%;
		height: 400px;
		background: transparent;
		color: var(--ink);
		outline: none;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
		font-size: 18px;
		margin-left: 30px;
		margin-top: 60px;
		margin-bottom: 80px;
		border: none;
	}

	.terminal-head {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
		color: var(--ink);
		border: none;
		box-shadow: none;
	}
	.counter {
		display: flex;
		align-items: center;
		gap: 8px;
		border-radius: 10px;
		margin: 0;
		transform: scale(0.7);
		margin-left: 400px;
		margin-bottom: 6px;
	}

	.terminal-body {
		height: 200px;
		overflow: auto;
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 8px;
		margin-left: 16px;
		border: none;
		box-shadow: none;
	}
	.trow {
		display: flex;
		gap: 8px;
		align-items: center;
		padding: 4px 2px;
		color: var(--ink);
	}
	.ticon-img {
		width: 16px;
		height: 16px;
		object-fit: contain;
	}

	.right {
		display: flex;
		width: 100%;
		flex-direction: column;
		gap: 12px;
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 8px;
	}
	.actions {
		display: flex;
		gap: 12px;
		justify-content: space-between;

		margin-right: 8px;
		margin-top: 6px;
		margin-bottom: 0px;
	}
	.btn {
		flex: 24;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 10px;
		cursor: pointer;
		scale: 1;
	}

	.table {
		height: 856px; /* retain table height like a textarea */
		display: flex;
		flex-direction: column;
		/* use the `editor` SVG asset for background */
		/* background-image: var(--table-img); */
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
	}
	.table-title {
		text-align: center;
		font-weight: 700;
		margin-bottom: 8px;
		/* margin-top: 48px; */

		border: none;
		box-shadow: none;
	}
	.table-head,
	.table-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 6px;
		border: none;
		box-shadow: none;
		/* margin-left: 32px; */
	}
	.table-head {
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 8px;
		font-weight: 600;
		margin-bottom: 8px;
		/* border: none;
		box-shadow: none; */
	}
	.table-body {
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 6px;
		flex: 1; /* occupy remaining space below the head */
		min-height: 0; /* allow flex child to shrink and enable scrolling */
		overflow-y: auto;
		overflow-x: hidden;
		display: flex;
		flex-direction: column;
		gap: 6px;
		/* 
		border: none;
		box-shadow: none; */
	}
	.table-row {
		border-bottom: 1px dashed rgba(255, 255, 255, 0.4);
		padding: 6px 4px;
	}
	.empty {
		opacity: 0.7;
		text-align: center;
		padding: 12px;
	}

	@media (max-width: 1130px) {
		.grid {
			grid-template-columns: 1fr;
		}
	}

	/* Strong CodeMirror overrides to ensure transparency and inherit panel background
   Use !important to beat CDN-loaded CodeMirror theme CSS if present */
	:global(.CodeMirror),
	:global(.CodeMirror-scroll),
	:global(.CodeMirror-gutters),
	:global(.CodeMirror pre) {
		background: transparent !important;
		color: inherit !important;
	}

	:global(.CodeMirror) {
		height: 100% !important;
		box-shadow: none !important;
		border: none !important;
		width: 97% !important;
		height: 400px !important;
		outline: none !important;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace !important;
		/* font-size: 18px !important; */
		margin-left: 10px !important;
		margin-top: 60px !important;
		margin-bottom: 80px !important;
		border: none !important;
	}

	:global(.CodeMirror-scroll) {
		/* disable horizontal scrolling and allow wrapping */
		overflow-x: hidden !important;
		overflow-y: auto !important;
		white-space: pre-wrap !important; /* allow wrap onto next line */
	}

	/* Make gutters transparent and inherit muted color */
	/* :global(.CodeMirror-gutters) {
		background: transparent !important;
		border-right: 4px solid var(--outline) !important;
		color: var(--ink-muted) !important;
	} */

	/* Apply the panel background image to the CodeMirror root so the editor shows your SVG */
	/* :global(.panel.editor .CodeMirror) {
		background-image: var(--editor-img) !important;
		background-position: left !important;
		background-repeat: no-repeat !important;
		background-size: auto !important;
	} */

	/* Ensure preformatted code uses the monospace font and no wrapping */
	:global(.CodeMirror pre) {
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace !important;
		font-size: 18px !important;
		line-height: 20px !important;
		padding: 0 8px !important;
		margin: 0 !important;
		white-space: pre-wrap !important; /* allow wrapped lines */
	}

	/* Cursor color per theme */
	:global(.ide[data-theme='dark'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #ffffff !important; /* white cursor for dark theme */
	}
	:global(.ide[data-theme='light'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #000000 !important; /* black cursor for light theme */
	}

	/* Error underline styling */
	:global(.error-underline) {
		border-bottom: 2px solid #ff0000 !important;
		background-color: rgba(255, 0, 0, 0.1) !important;
	}

	/* Platter language syntax highlighting (TypeScript standard colors) */
	:global(.cm-keyword-conditional) {
		color: #569cd6 !important; /* Blue for conditionals */
		font-weight: bold !important;
	}

	:global(.cm-keyword-logical) {
		color: #569cd6 !important; /* Blue for logical operators */
		font-weight: bold !important;
	}

	:global(.cm-keyword-loop) {
		color: #569cd6 !important; /* Blue for loops */
		font-weight: bold !important;
	}

	:global(.cm-keyword-control) {
		color: #569cd6 !important; /* Blue for control flow */
		font-weight: bold !important;
	}

	:global(.cm-keyword-method) {
		color: #dcdcaa !important; /* Yellow for methods */
		font-weight: bold !important;
	}

	:global(.cm-keyword-type) {
		color: #4ec9b0 !important; /* Cyan/Teal for data types */
		font-weight: bold !important;
	}

	:global(.cm-keyword-boolean) {
		color: #569cd6 !important; /* Blue for boolean */
		font-weight: bold !important;
	}

	:global(.cm-keyword-function) {
		color: #569cd6 !important; /* Blue for function definition */
		font-weight: bold !important;
	}

	:global(.cm-keyword-return) {
		color: #569cd6 !important; /* Blue for return */
		font-weight: bold !important;
	}

	:global(.cm-keyword-struct) {
		color: #569cd6 !important; /* Blue for struct */
		font-weight: bold !important;
	}

	:global(.cm-string) {
		color: #ce9178 !important; /* Orange/Tan for strings */
	}

	:global(.cm-number) {
		color: #b5cea8 !important; /* Light green for numbers */
	}

	:global(.cm-comment) {
		color: #6a9955 !important; /* Muted green for comments */
		font-style: italic !important;
	}

	:global(.cm-operator) {
		color: #d4d4d4 !important; /* Light gray for operators */
	}

	:global(.cm-variable) {
		color: #9cdcfe !important; /* Light blue for variables */
	}

	/* Operators */
	:global(.cm-operator-arithmetic) {
		color: #d4d4d4 !important; /* Light gray for arithmetic operators */
	}

	:global(.cm-operator-compound) {
		color: #d4d4d4 !important; /* Light gray for compound operators */
	}

	/* Delimiters */
	:global(.cm-delimiter) {
		color: #d4d4d4 !important; /* Light gray for delimiters */
	}

	/* Escape sequences */
	:global(.cm-escape-sequence) {
		color: #ce9178 !important; /* Orange/Tan for escape sequences */
		font-weight: bold !important;
	}
</style>
