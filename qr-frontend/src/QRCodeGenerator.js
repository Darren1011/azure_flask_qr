import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import 'bootstrap/dist/css/bootstrap.min.css';

const QRCodeGenerator = () => {
    const [textPrompt, setTextPrompt] = useState('');
    const [qrCodeData, setQrCodeData] = useState('');
    const [imagePrompt, setImagePrompt] = useState(null);
    const [outputImage, setOutputImage] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!textPrompt || !qrCodeData) {
            setError('Please fill in both the prompt and URL/Text fields.');
            return;
        }
        setError('');
        const formData = new FormData();
        formData.append('text_prompt', textPrompt);
        formData.append('qr_code_data', qrCodeData);
        if (imagePrompt) {
            formData.append('image_prompt', imagePrompt);
        }

        try {
            const response = await axios.post('http://127.0.0.1:5000/generate-qr', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setOutputImage(response.data.output.output_images[0]);
        } catch (error) {
            setError('Failed to generate QR code. Please try again.');
        }
    };

    const onDrop = (acceptedFiles) => {
        setImagePrompt(acceptedFiles[0]);
    };

    const { getRootProps, getInputProps } = useDropzone({ onDrop });

    return (
        <div className="container">
            <h1 className="text-center">AI QR Code Generator</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="prompt">Prompt</label>
                    <textarea
                        className="form-control"
                        id="prompt"
                        rows="3"
                        placeholder="Describe the subject/scene of the QR Code."
                        value={textPrompt}
                        onChange={(e) => setTextPrompt(e.target.value)}
                    ></textarea>
                </div>
                <div className="form-group">
                    <label htmlFor="urlOrText">URL or Text</label>
                    <input
                        type="text"
                        className="form-control"
                        id="urlOrText"
                        placeholder="Enter your URL/Text below."
                        value={qrCodeData}
                        onChange={(e) => setQrCodeData(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="referenceImage">Reference Image <small>(optional)</small></label>
                    <div {...getRootProps({ className: 'dropzone' })}>
                        <input {...getInputProps()} />
                        <p>Drop files here, browse files or import from:</p>
                    </div>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button type="submit" className="btn btn-primary btn-block">Submit</button>
            </form>
            {outputImage && (
                <div className="text-center mt-4">
                    <h2>Generated QR Code</h2>
                    <img src={outputImage} alt="Generated QR Code" />
                    <a href={outputImage} download className="btn btn-secondary mt-2">Download</a>
                </div>
            )}
        </div>
    );
};

export default QRCodeGenerator;