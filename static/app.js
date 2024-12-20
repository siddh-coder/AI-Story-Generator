async function askGPT() {
    const question = document.getElementById('gpt-question').value;
    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });
    const data = await response.json();
    document.getElementById('gpt-answer').textContent = data.answer;
}

async function generateImage() {
    const prompt = document.getElementById('image-prompt').value;
    const spinner = document.getElementById('loading-spinner');
    const imgElement = document.getElementById('generated-image');
    
    // Show spinner and clear previous image
    spinner.style.display = 'block';
    imgElement.src = '';

    try {
        const response = await fetch('/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt }),
        });

        const data = await response.json();
        if (data.image_base64) {
            imgElement.src = `data:image/png;base64,${data.image_base64}`;
        } else {
            alert('Error generating image.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating the image.');
    } finally {
        // Hide spinner
        spinner.style.display = 'none';
    }
}
}


