import pytest

def consume_response(response):
                                                                                 
    list(response.iter_encoded())
    response.close()

def test_admin_export(authenticated_admin_client, db_session, pending_user):
                                           
    response = authenticated_admin_client.get("/admin/users/export")
    assert response.status_code == 200
    consume_response(response)

    response = authenticated_admin_client.get("/admin/users/export?status_filter=pending")
    assert response.status_code == 200
    consume_response(response)

    response = authenticated_admin_client.get("/admin/users/export?status_filter=approved")
    assert response.status_code == 200
    consume_response(response)

    response = authenticated_admin_client.get("/admin/users/export?status_filter=blacklisted")
    assert response.status_code == 200
    consume_response(response)

    response = authenticated_admin_client.get("/admin/users/export?role_filter=employee")
    assert response.status_code == 200
    consume_response(response)

                                                    
    response = authenticated_admin_client.get("/admin/")
    assert response.status_code == 200
