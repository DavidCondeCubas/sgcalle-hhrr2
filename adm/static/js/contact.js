(function(){
	"use strict";
	var contador = -1;
	
	function toggleContactType(){
		var contact_id_select = this.parentNode.parentNode.querySelector("select[name='contact_existing_id']");
		var new_contact_form = this.parentNode.parentNode.parentNode.querySelector("div.new-contact-form");
		if(this.value == "new"){
			contact_id_select.disabled=true;
			new_contact_form.style.display = "flex";

			$(new_contact_form).find("select, input").prop("disabled", false);
			
		}else if(this.value == "existing"){
			contact_id_select.disabled=false;
			new_contact_form.style.display = "none";
			$(new_contact_form).find("select, input").prop("disabled", true);
		}
	}
	
	function addContact() {
		var contactClonnable = document.getElementById("form-template").cloneNode(true);
		var contactForms = document.getElementById("contact_forms");
	
		var existingValues = [];
		$(contactForms).find("select[name='contact_existing_id']").each(function(index, data){
			if (!$(this).prop("disabled")) {
				$(contactClonnable).find("select[name='contact_existing_id']")
								   .find("option[value='"+$(this).val()+"']").remove();
			} 
		})
		
		contactForms.appendChild(contactClonnable)
		var contact_type_select = contactClonnable.querySelector("select[name='contact_type_select']");
		contact_type_select.addEventListener("change",toggleContactType);
//		$(toggleContactType).trigger("change");
		
	// $(contactClonnable).find("").on("disabled", true);
	// $(contactClonnable).find("select[name='contact_id']").prop("disabled",
	// true);
		
		contador--;
		$(contactClonnable).attr("id", "relationship_" + contador)
		$(contactClonnable).removeClass("d-none");
		var removeButton = $(contactClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeContact);
	
		$(this).remove();
	
		$("#contact_forms").append("<button type='button' class='add-contact btn btn-success d-block m-auto'>Add Contact</button>");
		$(".add-contact").on("click", addContact);
	}
	
	function changeState() {
		var select_state = $(this).parents("div.row").find("select.state")
		select_state.children("option:gt(0)").hide();
		select_state.children("option[data-country='" + $(this).val() + "']").show();
	
		if (select_state.children("option:selected").is(":hidden")){
			select_state.children("option:nth(0)").prop("selected", true);
		}
	}
	
	function removeContact() {
		var id = $(this).data("id");
		$("#relationship_" + id).remove();
		$(this).remove();
	}
	

	function disableCheckboxes(){
//		event.preventDefault();
		
		$(this).find(".true-emergency-contact").each(function(){
			if(this.checked){
				$(this).next(".false-emergency-contact")[0].disabled = true
			}
		})
		
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
		var event = document.createEvent('HTMLEvents');
		event.initEvent(eventName, true, false);
		nodeIterate(nodeList, function(element){
			element.dispatchEvent(event);
		})
	}
	ready(function() {
		addEvent(document.querySelectorAll(".add-contact"), "click", addContact);
		addEvent(document.querySelectorAll(".remove-contact"), "click", removeContact);
		addEvent(document.querySelectorAll("select.country"), "change", changeState);
		// triggerEvent(document.querySelectorAll("select.country"), "change");

		document.getElementById("family_form").addEventListener("submit", disableCheckboxes);
	});
})()