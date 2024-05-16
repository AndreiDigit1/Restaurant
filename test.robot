*** Settings ***
Library    RequestsLibrary
Library    OperatingSystem
Library    Collections

*** Variables ***
${BASE_URL}    http://127.0.0.1:5000

*** Test Cases ***
Test Menu Route
    [Documentation]    ruta /menu_route
    Create Session    restaurant    ${BASE_URL}
    ${response}=    GET    http://127.0.0.1:5000/menu_route
    Should Be Equal As Strings    ${response.status_code}    200
    ${menu}=    Evaluate    json.loads("""${response.content}""")    json
    Log    ${menu}
    Should Contain    ${menu}    dishes
    Should Contain    ${menu}    drinks

Test Create Reservation Route
    [Documentation]    ruta /createReservation
    Create Session    restaurant    ${BASE_URL}
    ${data}=    Create Dictionary    number_clients=2    reservation_time=2024-05-12
    ${response}=    POST    http://127.0.0.1:5000/createReservation    data=${data}
    Should Be Equal As Strings    ${response.status_code}    200
    Log    ${response.content}

Test Create Reservation Invalid Data Route
    [Documentation]    creare de rezervare cu peste 5 clienti
    Create Session    reservation    ${BASE_URL}
    ${data}=    Create Dictionary    number_clients=7    reservation_time=2024-07-07
    ${response}=    POST    ${BASE_URL}/createReservation    data=${data}    expected_status=any
    Log To Console    ${response.content}
    ${content}=    Convert To String    ${response.content}
    Should Contain    ${content}    Maxim five clients for a reservation!

Test Create Reservation Invalid Data Route
    [Documentation]    creare de rezervare cu o data invalida
    Create Session    reservation    ${BASE_URL}
    ${data}=    Create Dictionary    number_clients=3    reservation_time=2023-02-01
    ${response}=    POST    ${BASE_URL}/createReservation    data=${data}    expected_status=any
    Log To Console    ${response.content}
    ${content}=    Convert To String    ${response.content}
    Should Contain    ${content}    The date must be greater than the current date!


Test Users Route
    [Documentation]    Ruta /users
    Create Session    users    ${BASE_URL}
    ${response}=    GET    ${BASE_URL}/users    expected_status=200
    Log    ${response.content}
    ${users}=    Evaluate    json.loads("""${response.content}""")    json
    Should Not Be Empty    ${users}
    ${first_user}=    Get From List    ${users}    0
    Dictionary Should Contain Key    ${first_user}    id
    Dictionary Should Contain Key    ${first_user}    name
    Dictionary Should Contain Key    ${first_user}    email
    [Teardown]    Delete All Sessions

Test Ratings Route
    [Documentation]    Ruta /ratings
    Create Session    ratings    ${BASE_URL}
    ${response}=    GET    ${BASE_URL}/ratings    expected_status=200
    ${response_content}=    Convert To String    ${response.content}
    Log    ${response_content}
    Should Contain    ${response_content}    <h1>Ratings</h1>
    [Teardown]    Delete All Sessions

