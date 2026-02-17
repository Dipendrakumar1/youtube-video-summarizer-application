import React from 'react';
import Tabs from "./Tabs";


class BackendAPI extends React.Component {

	constructor(props) {
		super(props);
		this.state = {
			name: '',
			error: null,
			isLoaded: false,
			isLoading: false,
			failedMessage: null,
			englishTranscript: [],
			hindiTranscript: [],
			originalTextLength: 0,
			summarizedTextLength: 0
		};
	}

	handleChange = (event) => {

		this.setState({ [event.target.name]: event.target.value });
	}

	downloadFile = (content, filename) => {
		const element = document.createElement("a");
		const file = new Blob([content], { type: 'text/plain' });
		element.href = URL.createObjectURL(file);
		element.download = filename;
		document.body.appendChild(element); // Required for this to work in FireFox
		element.click();
		document.body.removeChild(element);
	}

	handleSubmit = (event) => {

		this.setState({
			isLoading: true,
			isLoaded: false
		});

		const apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001/api/';
		var FinalURL = `${apiBaseUrl}?video_url=${this.state.name}`;

		fetch(FinalURL)
			.then(res => res.json())
			.then(
				(result) => {
					// Check for success based on the new backend structure
					// Success: { data: { message: "Success", ... } }
					// Error: { status: "Failed", message: "..." }

					if (result.data && result.data.message === "Success") {
						this.setState({
							isLoaded: true,
							isLoading: false,
							message: "Success",
							englishTranscript: result.data.eng_summary,
							hindiTranscript: result.data.hind_summary,
							originalTextLength: result.data.original_txt_length,
							summarizedTextLength: result.data.final_summ_length,
						});
					} else {
						// Handle error (either from top-level or nested if we reverted logic)
						this.setState({
							isLoaded: true,
							isLoading: false,
							infoMessage: result.message || "Unknown error",
							failedMessage: result.message || "Unknown error"
						});
					}
				},

				(error) => {
					this.setState({
						isLoaded: true,
						isLoading: false,
						error: error,
						failedMessage: "Network error or API unreachable"
					});
				}
			)

		event.preventDefault();
	}

	stopAudio = () => {

		window.speechSynthesis.cancel();
	}

	textToAudio = () => {

		var synth = window.speechSynthesis;
		const text = Array.isArray(this.state.englishTranscript)
			? this.state.englishTranscript.join(' ')
			: this.state.englishTranscript;
		var utterance = new SpeechSynthesisUtterance(text);
		synth.speak(utterance);

	}

	render() {

		const { isLoaded, isLoading, message, englishTranscript, hindiTranscript, originalTextLength, summarizedTextLength } = this.state;

		if (isLoading) {
			return (
				<>
					<form onSubmit={this.handleSubmit}>
						<label>Video URL:</label>
						<input className="input-1" type="url" value={this.state.value} placeholder="Paste your YouTube Video link here." name="name" onChange={this.handleChange} required autoComplete="off" />
						<input className="submit-1" type="submit" value="Summarize" />
					</form>
					<div className="center-div">
						<div className="lds-ripple"><div></div><div></div></div>
					</div>
					<Tabs>
						<div label="English">
							<div className="tab-content-1">
								English Summarized Text Will be Shown Here...
							</div>
						</div>
						<div label="Hindi">
							<div className="tab-content-1">
								Hindi Summarized Text Will be Shown Here...
							</div>
						</div>
					</Tabs>
				</>
			);
		} else if (isLoaded) {

			if (message === "Success") {
				return (
					<>
						<form onSubmit={this.handleSubmit}>
							<label>Video URL:</label>
							<input className="input-1" type="url" value={this.state.value} placeholder="Paste your YouTube Video link here." name="name" onChange={this.handleChange} required autoComplete="off" />
							<input className="submit-1" type="submit" value="Summarize" />
						</form>
						<p>{originalTextLength}<i className="arrow right"></i>{summarizedTextLength}</p>
						<Tabs>
							<div label="English">
								<div className="tab-content">
									<ul>
										{Array.isArray(englishTranscript) ? (
											englishTranscript.map((sentence, index) => (
												<li key={index} style={{ marginBottom: '10px' }}>{sentence}</li>
											))
										) : (
											<li>{englishTranscript}</li>
										)}
									</ul>
									<div className="center-div" style={{ marginTop: '20px' }}>
										<button className="button-29" type="button" onClick={this.textToAudio}>Speak</button>
										<button className="button-29" type="button" onClick={this.stopAudio} style={{ marginLeft: '10px' }}>Stop</button>
										<button
											className="buttonDownload"
											type="button"
											style={{ marginLeft: '10px' }}
											onClick={() => {
												const content = Array.isArray(englishTranscript) ? englishTranscript.join('\n') : englishTranscript;
												this.downloadFile(content, "English_Transcript.txt")
											}}
										>
											Download
										</button>
									</div>
								</div>
							</div>
							<div label="Hindi">
								<div className="tab-content">
									<ul>
										{Array.isArray(hindiTranscript) ? (
											hindiTranscript.map((sentence, index) => (
												<li key={index} style={{ marginBottom: '10px' }}>{sentence}</li>
											))
										) : (
											<li>{hindiTranscript}</li>
										)}
									</ul>
									<div className="center-div" style={{ marginTop: '20px' }}>
										<button
											className="buttonDownload"
											type="button"
											onClick={() => {
												const content = Array.isArray(hindiTranscript) ? hindiTranscript.join('\n') : hindiTranscript;
												this.downloadFile(content, "Hindi_Transcript.txt")
											}}
										>
											Download
										</button>
									</div>
								</div>
							</div>
						</Tabs>
					</>
				);
			} else {
				return (
					<>
						<form onSubmit={this.handleSubmit}>
							<label>Video URL:</label>
							<input className="input-1" type="url" value={this.state.value} placeholder="Paste your YouTube Video link here." name="name" onChange={this.handleChange} required autoComplete="off" />
							<input className="submit-1" type="submit" value="Summarize" />
						</form>
						<div style={{ color: 'var(--error-color)', marginBottom: '20px' }}>
							An Error occured: {this.state.failedMessage}.
						</div>
						<Tabs>
							<div label="English">
								<div className="tab-content-1">
									English Summarized Text Will be Shown Here...
								</div>
							</div>
							<div label="Hindi">
								<div className="tab-content-1">
									Hindi Summarized Text Will be Shown Here...
								</div>
							</div>
						</Tabs>
					</>
				);
			}

		} else {
			return (
				<>
					<form onSubmit={this.handleSubmit}>
						<label>Video URL:</label>
						<input className="input-1" type="url" value={this.state.value} placeholder="Paste your YouTube Video link here." name="name" onChange={this.handleChange} required autoComplete="off" />
						<input className="submit-1" type="submit" value="Summarize" />
					</form>
					<p>Original Length<i className="arrow right"></i>Final Length</p>
					<Tabs>
						<div label="English">
							<div className="tab-content-1">
								English Summarized Text Will be Shown Here...
							</div>
						</div>
						<div label="Hindi">
							<div className="tab-content-1">
								Hindi Summarized Text Will be Shown Here...
							</div>
						</div>
					</Tabs>
				</>
			);
		}
	}
}

export default BackendAPI;