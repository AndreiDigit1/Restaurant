function showSearchForm(type) {
    document.getElementById('search_name_form').style.display = 'none';
    document.getElementById('search_reservations_form').style.display = 'none';
    document.getElementById('search_phone_form').style.display = 'none';

    if (type === 'name') {
        document.getElementById('search_name_form').style.display = 'block';
    } else if (type === 'reservations') {
        document.getElementById('search_reservations_form').style.display = 'block';
    } else if (type === 'phone') {
        document.getElementById('search_phone_form').style.display = 'block';
    }
}
