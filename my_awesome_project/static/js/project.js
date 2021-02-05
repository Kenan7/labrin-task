// /* Project specific Javascript goes here. */
// var filelist = document.getElementById('file-list');

// const animateCSS = (element, animation, prefix = 'animate__') =>
// 	// We create a Promise and return it
// 	new Promise((resolve, reject) => {
// 		const animationName = `${prefix}${animation}`;
// 		const node = document.querySelector(element);

// 		node.classList.add(`${prefix}animated`, animationName);

// 		// When the animation ends, we clean the classes and resolve the Promise
// 		function handleAnimationEnd(event) {
// 			event.stopPropagation();
// 			node.classList.remove(`${prefix}animated`, animationName);
// 			resolve('Animation ended');
// 		}

// 		node.addEventListener('animationend', handleAnimationEnd, { once: true });
// 	});

// setInterval(function() {
// 	animateCSS('.filee', 'fadeOut');
// 	filelist.style.opacity = '0';

// 	setTimeout(function() {
// 		animateCSS('.filee', 'fadeIn');
// 	}, 1000);
// }, 4000);

// // setInterval(function() {
// // 	filelist.classList.add('animate__fadeOut');
// // 	setTimeout(function() {
// // 		filelist.classList.remove('animate__fadeOut');
// // 		filelist.classList.add('animate__fadeInDown');
// // 	}, 2000);
// // 	filelist.classList.remove('animate__fadeInDown');
// // }, 5000);
