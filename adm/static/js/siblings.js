var contador = -1;

function addSibling() {
	var siblingClonnable = document.getElementById("form-template").cloneNode(
			true);
	var siblingForms = document.getElementById("sibling_forms");

	siblingForms.appendChild(siblingClonnable)

	contador--;
	$(siblingClonnable).attr("id", "previous_sibling_" + contador)
	$(siblingClonnable).removeClass("d-none");
	var removeButton = $(siblingClonnable).find("button")
	$(removeButton).data("id", contador).on("click", removeSibling);

	$(this).remove();

	$("#sibling_forms").append("<button type='button' class='add-sibling btn btn-success d-block m-auto'>Add Sibling</button>");
	$(".add-sibling").on("click", addSibling);
}

function changeState() {
	var select_state = $(this).parents("div.row").find("select.state")
	select_state.children("option:gt(0)").hide();
	select_state.children("option[data-country='" + $(this).val() + "']").show();

	if (select_state.children("option:selected").is(":hidden")){
		select_state.children("option:nth(0)").prop("selected", true);
	}
}

function removeSibling() {
	id = $(this).data("id");
	$("#previous_sibling_" + id).remove();
	$(this).remove();
}

$(document).ready(function() {
	$(".add-sibling").on("click", addSibling);
	$(".remove-sibling").on("click", removeSibling);
	$("select.country").on("change", changeState);
	$("select.country").trigger("change");
});