jQuery(function($){

    function set_cookie( name, value ) {
        document.cookie = name + "=" + value + ";" + ";path=/";
    }

    function delete_cookie( name ) {
        document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }

    $('.sidebar-menu-toggle-btn').click(function(){

        if( $(document.body).hasClass('sidebar-menu-closed') ){
            $(document.body).removeClass('sidebar-menu-closed');
            delete_cookie( 'sidebar_menu_closed' );
        }
        else{
            $(document.body).addClass('sidebar-menu-closed');
            set_cookie( 'sidebar_menu_closed', '1' );
        }
    });
});