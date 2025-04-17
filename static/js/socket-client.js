import io from 'socket.io-client';

const socket = io.connect('http://localhost:5000');

// Listen for button state updates from the server
socket.on('button_config_updated', (data) => {
    console.log('Button config updated:', data);
    // Update the button state in the frontend
    updateButtonState(data);
});

// Function to update button state in the frontend
function updateButtonState(data) {
    const button = document.getElementById(data.id);
    if (button) {
        button.style.transform = `translate3d(${data.position.x}px, ${data.position.y}px, ${data.position.z}px) rotateX(${data.rotation.x}deg) rotateY(${data.rotation.y}deg) rotateZ(${data.rotation.z}deg) scale(${data.scale})`;
    }
}

// Emit button interaction events to the server
function emitButtonInteraction(buttonId, interactionType) {
    socket.emit('button_interaction', {
        button_id: buttonId,
        type: interactionType
    });
}

// Example usage: emit a button click event
document.getElementById('exampleButton').addEventListener('click', () => {
    emitButtonInteraction('exampleButton', 'click');
});
