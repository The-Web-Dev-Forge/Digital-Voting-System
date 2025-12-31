function search() {
    const category = document.getElementById('category').value;
    const subcategory = document.getElementById('subcategory').value;
    const keyword = document.getElementById('keyword').value;
    const startdate = document.getElementById('startdate').value;
    const todate = document.getElementById('todate').value;
    const division = document.getElementById('division').value;

    console.log('Search Parameters:');
    console.log('Category:', category);
    console.log('Subcategory:', subcategory);
    console.log('Keyword:', keyword);
    console.log('Start Date:', startdate);
    console.log('To Date:', todate);
    console.log('Division:', division);

    alert('Search form has been submitted!');
}

function resetForm() {
    document.getElementById('search-form').reset();
    alert('Form has been reset!');
}
