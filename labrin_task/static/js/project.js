// Mirkenan

// window.onload = loadWhateverNeeded();

// function loadWhateverNeeded() {}

setTimeout(function() {
	let field = document.getElementById('create_file_name_field');
	field.removeAttribute('required');
}, 1500);

Dropzone.options.customDropzone = {
	// the page will reload once the upload is completed
	init : function() {
		this.on('complete', function(file) {
			location.reload();
		});
	}
};
