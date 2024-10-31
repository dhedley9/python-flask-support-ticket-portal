jQuery( function($){

    $('#register_password').on('input', function(){
        
        let value = $(this).val();

        $('.password-strength-criteria').removeClass('passed');

        if( value.length > 8 ){
            $('.password-strength-criteria.length').addClass('passed');
        }

        if( value.match(/[a-z]/) ){
            $('.password-strength-criteria.lowercase').addClass('passed');
        }

        if( value.match(/[A-Z]/) ){
            $('.password-strength-criteria.uppercase').addClass('passed');
        }

        if( value.match(/[0-9]/) ){
            $('.password-strength-criteria.number').addClass('passed');
        }

        if( value.match(/[^a-zA-Z0-9]/) ){
            $('.password-strength-criteria.special').addClass('passed');
        }
    });
});