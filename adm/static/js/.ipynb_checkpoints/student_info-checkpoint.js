(function(){
	"use strict";

	function disableElementsInForm(event) {
		event.preventDefault();
		document.getElementById("info-form").submit();
	}

	function ready(fn) {
		if (document.readyState != 'loading'){
			fn();
		} else {
			document.addEventListener('DOMContentLoaded', fn);
		}
	}

	ready(function() {
		document.getElementById("info-form").addEventListener("submit",
				disableElementsInForm);
	});
})();