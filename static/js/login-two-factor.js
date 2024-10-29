jQuery( function($) {

    $('.two-factor-code input').on('input', function() {

        if ($(this).val().length === 1) {

            let next = $(this).next("input");

            if( next.length ) {
                next.focus();
                return;
            }

            next = $(this).closest('.two-factor-code-digits').nextAll('.two-factor-code-digits').find('input:first');

            if( next.length ) {
                next.focus();
                return;
            }
        }
    });

    $('.two-factor-code input[name="two_factor_code_digit_1"]').on( 'paste', function(event) {

        let paste = (event.originalEvent.clipboardData || window.clipboardData).getData("text");

        $('.two-factor-code input').each( function( index, element ) {
            
            $(this).val( paste[index] );
            $(this).focus();
        });
    });
});