window.addEventListener('DOMContentLoaded', () => {
    const gameContainer = document.getElementById('game-container');
    const level = document.getElementById('level');
    const entrance = document.getElementById('entrance');
    const exit = document.getElementById('exit');
  
    gameContainer.addEventListener('mousemove', (event) => {
      const containerRect = gameContainer.getBoundingClientRect();
      const mouseX = event.clientX - containerRect.left;
      const mouseY = event.clientY - containerRect.top;
  
      // Scroll the game container when mouse reaches the edges
      const scrollSpeed = 10;
      const scrollThreshold = 100;
      if (mouseX < scrollThreshold) {
        gameContainer.scrollLeft -= scrollSpeed;
      } else if (mouseX > containerRect.width - scrollThreshold) {
        gameContainer.scrollLeft += scrollSpeed;
      }
      if (mouseY < scrollThreshold) {
        gameContainer.scrollTop -= scrollSpeed;
      } else if (mouseY > containerRect.height - scrollThreshold) {
        gameContainer.scrollTop += scrollSpeed;
      }
    });
  });
  