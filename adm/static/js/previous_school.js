(function(){
	"use strict";
	var contador = -1;

	function addSchool() {
		var schoolClonnable = document.getElementById("form-template").cloneNode(
				true);
		var schoolForms = document.getElementById("school_forms");

		schoolForms.appendChild(schoolClonnable);

		contador--;

		schoolClonnable.id = "previous_school_" + contador;
		$(schoolClonnable).removeClass("d-none");
		var removeButton = $(schoolClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeSchool);

		$(this).remove();


		$("#school_forms").append("<button type='button' class='add-school btn btn-success d-block m-auto'>Add School</button>");
		$(".add-school").on("click", addSchool);
		var countryElement = document.querySelectorAll("select.country");
		addEvent(countryElement, "change", changeState);
		triggerEvent(countryElement, "change");
	}

	function changeState() {
		var select_state = this.closest("div.row").querySelector("select.state");
		var select_country = this;
		var set_options = function(element){
			if (element.dataset.country === element.value){
				console.log("QUESO");	
			}
		};

		select_state.querySelectorAll("option").forEach(set_options);
		// nodeIterate(select_state.querySelectorAll("option"), set_options);

		/* select_state.children("option:gt(0)").hide();
		select_state.children("option[data-country='" + $(this).val() + "']").show();

		if (select_state.ch:ildren("option:selected").is(":hidden")){
			select_state.children("option:nth(0)").prop("selected", true);
		} */
	}

	function removeSchool() {
		var id = $(this).data("id");
		$("#previous_school_" + id).remove();
		$(this).remove();
	}

	function ready(fn) {
		if (document.readyState != 'loading'){
			fn();
		} else {
			document.addEventListener('DOMContentLoaded', fn);
		}
	}

	function nodeIterate(nodeList, functionCallback) {
		var i = nodeList.length;
		while (i){
			functionCallback(nodeList[--i]);
		}
	}

	function addEvent(nodeList, event, fn){
		nodeIterate(nodeList, function(element){
			element.addEventListener(event, fn);
		});

	}

	function triggerEvent(nodeList, eventName){
		var event = new Event(eventName, {"bubbles": true, "cancelable": false})
		nodeIterate(nodeList, function(element){
			element.dispatchEvent(event);
		})
	}

	ready(function() {
		addEvent(document.querySelectorAll(".add-school"), "click", addSchool);
		addEvent(document.querySelectorAll(".remove-school"), "click", removeSchool);
		addEvent(document.querySelectorAll("select.country"), "change", changeState);
		
		document.querySelector
		triggerEvent(document.querySelectorAll("select.country"), "change");
	});
})();