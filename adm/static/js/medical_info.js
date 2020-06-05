(function () {
	"use strict";
	var contador = -1;

	function addMedicalCondition() {
		var medicalConditionClonnable = document.getElementById("form-template-condition").cloneNode(true);
		var medicalConditionForms = document.getElementById("form-condition");

		medicalConditionForms.insertBefore(medicalConditionClonnable, this)
		//medicalConditionForms.appendChild(medicalConditionClonnable)

		contador--;
		$(medicalConditionClonnable).attr("id", "medical_condition_" + contador)
		$(medicalConditionClonnable).removeClass("d-none");
		var removeButton = $(medicalConditionClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeMedicalCondition);

		// $(".add-medical_condition").on("click", addMedicalCondition);
		$(medicalConditionForms).find("select.country").on("change", changeState);
	}

	function addMedicalAllergy() {
		var medicalAllergyClonnable = document.getElementById("form-template-allergy").cloneNode(true);
		var medicalAllergyForms = document.getElementById("form-allergy");

		medicalAllergyForms.insertBefore(medicalAllergyClonnable, this)
		//medicalAllergyForms.appendChild(medicalAllergyClonnable)

		contador--;
		$(medicalAllergyClonnable).attr("id", "medical_allergy_" + contador)
		$(medicalAllergyClonnable).removeClass("d-none");
		var removeButton = $(medicalAllergyClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeMedicalAllergy);

		// $(".add-medical_allergy").on("click", addMedicalAllergy);
		$(medicalAllergyForms).find("select.country").on("change", changeState);
	}

	function addMedicalMedication() {
		var medicalMedicationClonnable = document.getElementById("form-template-medication").cloneNode(true);
		var medicalMedicationForms = document.getElementById("form-medication");

		medicalMedicationForms.insertBefore(medicalMedicationClonnable, this)
		//medicalMedicationForms.appendChild(medicalMedicationClonnable)

		contador--;
		$(medicalMedicationClonnable).attr("id", "medical_medication_" + contador)
		$(medicalMedicationClonnable).removeClass("d-none");
		var removeButton = $(medicalMedicationClonnable).find("button")
		$(removeButton).data("id", contador).on("click", removeMedicalMedication);

		// $(".add-medical_medication").on("click", addMedicalMedication);
		$(medicalMedicationForms).find("select.country").on("change", changeState);
	}

	function changeState() {
		var select_state = $(this).parents("div.row").find("select.state")
		select_state.children("option:gt(0)").hide();
		select_state.children("option[data-country='" + $(this).val() + "']").show();

		if (select_state.children("option:selected").is(":hidden")) {
			select_state.children("option:nth(0)").prop("selected", true);
		}
	}

	function removeMedicalCondition() {
		var id = $(this).data("id");
		$("#medical_condition_" + id).remove();
		$(this).remove();
	}
	function removeMedicalAllergy() {
		var id = $(this).data("id");
		$("#medical_allergy_" + id).remove();
		$(this).remove();
	}
	function removeMedicalMedication() {
		var id = $(this).data("id");
		$("#medical_medication_" + id).remove();
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
		var event = document.createEvent('HTMLEvents');
		event.initEvent(eventName, true, false);
		nodeIterate(nodeList, function(element){
			element.dispatchEvent(event);
		})
	}

	ready(function () {
		addEvent(document.querySelectorAll(".add-medical_condition"), "click", addMedicalCondition);
	 	addEvent(document.querySelectorAll(".remove-medical_condition"), "click", removeMedicalCondition);
 
		addEvent(document.querySelectorAll(".add-medical_allergy"), "click", addMedicalAllergy);
		addEvent(document.querySelectorAll(".remove-medical_allergy"), "click", removeMedicalAllergy);

		addEvent(document.querySelectorAll(".add-medical_medication"), "click", addMedicalMedication);
		addEvent(document.querySelectorAll(".remove-medical_medication"), "click", removeMedicalMedication);

		addEvent(document.querySelectorAll("select.country"), "change", changeState);
		triggerEvent(document.querySelectorAll("select.country"), "change");
	});
}
)();