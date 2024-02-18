// Hide submenus
$('#react-container .collapse').collapse('hide');
// Collapse/Expand icon
$('#collapse-icon').addClass('fa-angle-double-left');
// Collapse click
$('[data-toggle=sidebar-collapse]').click(function() {
	// alert('clicked')
	SidebarCollapse();
});

function SidebarCollapse() {
	$('.menu-collapsed').toggleClass('d-none');
	$('.sidebar-submenu').toggleClass('d-none');
	$('.submenu-icon').toggleClass('d-none');
	$('#sidebar-container').toggleClass('sidebar-expanded sidebar-collapsed');
	// Treating d-flex/d-none on separators with title
	var SeparatorTitle = $('.sidebar-separator-title');
	if (SeparatorTitle.hasClass('d-flex')) {
		SeparatorTitle.removeClass('d-flex');
	} else {
		SeparatorTitle.addClass('d-flex');
	}
	// Collapse/Expand icon
	$('#collapse-icon').toggleClass('fa-angle-double-left fa-angle-double-right');
}

document.addEventListener("DOMContentLoaded", function(event) {
	// alert('Hey')
  });

var websiteStatus = "development"; // or "production"

window.onload = function() {
    var statusElement = document.getElementById("status-icon");
    var iconElement = statusElement.querySelector(".fa");
    var anchorElement = statusElement.querySelector("a");

    if (websiteStatus === "development") {
        iconElement.classList.add("fa-wrench");
        anchorElement.textContent = " Development";
        // Set the color for the icon and text to orange programmatically
        iconElement.style.color = "orange";
        anchorElement.style.color = "orange";
    } else if (websiteStatus === "production") {
        iconElement.classList.add("fa-check-circle", "text-success");
        anchorElement.textContent = " Production";
    }
};