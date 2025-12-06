/**
 * New Year's Countdown Timer
 * Calculates and displays time remaining until January 1st
 */

// Function to calculate time remaining
function updateCountdown() {
    // Get current date
    const now = new Date();
    
    // Determine target New Year date
    const currentYear = now.getFullYear();
    let targetYear = currentYear + 1;
    
    // If we're already past January 1st of current year, target next year
    // If we're before January 1st of current year, target current year
    const newYear = new Date(targetYear, 0, 1, 0, 0, 0);
    
    // Calculate time difference in milliseconds
    const timeDifference = newYear - now;
    
    // Check if countdown is complete
    if (timeDifference <= 0) {
        displayHappyNewYear();
        return;
    }
    
    // Calculate time units
    const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
    const hours = Math.floor((timeDifference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);
    
    // Update DOM elements with padded values
    document.getElementById('days').textContent = padZero(days);
    document.getElementById('hours').textContent = padZero(hours);
    document.getElementById('minutes').textContent = padZero(minutes);
    document.getElementById('seconds').textContent = padZero(seconds);
}

// Function to pad single digit numbers with leading zero
function padZero(num) {
    return num.toString().padStart(2, '0');
}

// Function to display Happy New Year message
function displayHappyNewYear() {
    const countdownTitle = document.querySelector('.countdown-title');
    const countdownTimer = document.querySelector('.countdown-timer');
    
    if (countdownTitle) {
        countdownTitle.textContent = '🎉 Happy New Year! 🎉';
        countdownTitle.style.fontSize = 'clamp(2rem, 5vw, 3rem)';
        countdownTitle.style.animation = 'pulseGlow 1s ease-in-out infinite';
    }
    
    if (countdownTimer) {
        countdownTimer.innerHTML = `
            <div style="text-align: center; width: 100%;">
                <div style="font-size: clamp(3rem, 8vw, 5rem); margin-bottom: 1rem;">🎊</div>
                <div style="font-size: clamp(1.5rem, 4vw, 2rem); color: var(--gold);">
                    Welcome to ${new Date().getFullYear()}!
                </div>
            </div>
        `;
    }
}

// Add smooth entrance animation
function animateCountdown() {
    const timeUnits = document.querySelectorAll('.time-unit');
    timeUnits.forEach((unit, index) => {
        unit.style.opacity = '0';
        unit.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            unit.style.transition = 'all 0.5s ease-out';
            unit.style.opacity = '1';
            unit.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Initialize countdown
function initCountdown() {
    // Initial update
    updateCountdown();
    
    // Animate entrance
    setTimeout(animateCountdown, 500);
    
    // Update every second
    setInterval(updateCountdown, 1000);
}

// Start countdown when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCountdown);
} else {
    initCountdown();
}

// Optional: Add celebration effects when reaching specific milestones
function checkMilestone() {
    const now = new Date();
    const currentYear = now.getFullYear();
    const newYear = new Date(currentYear + 1, 0, 1, 0, 0, 0);
    const timeDifference = newYear - now;
    const hoursRemaining = timeDifference / (1000 * 60 * 60);
    
    // Trigger special effects for milestones
    if (hoursRemaining <= 24 && hoursRemaining > 23.99) {
        console.log('🎉 Less than 24 hours to New Year!');
    } else if (hoursRemaining <= 1 && hoursRemaining > 0.99) {
        console.log('🎊 Final hour approaching!');
    }
}

// Check milestones every minute
setInterval(checkMilestone, 60000);
