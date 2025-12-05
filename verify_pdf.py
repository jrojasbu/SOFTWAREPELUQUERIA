import requests
import os
from app import app

def test_pdf_generation():
    # Create a test client
    with app.test_client() as client:
        # Make a request to the export_pdf route
        response = client.get('/export_pdf')
        
        # Check if the response is successful
        if response.status_code == 200:
            print("Success: Response code is 200")
            
            # Check content type
            if response.content_type == 'application/pdf':
                print("Success: Content-Type is application/pdf")
                
                # Check if content is not empty
                if len(response.data) > 0:
                    print(f"Success: PDF generated with size {len(response.data)} bytes")
                    
                    # Save to a file to manually inspect if needed (optional)
                    with open('test_output.pdf', 'wb') as f:
                        f.write(response.data)
                    print("Success: Saved test_output.pdf")
                else:
                    print("Error: PDF content is empty")
            else:
                print(f"Error: Unexpected Content-Type: {response.content_type}")
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print(response.data)

if __name__ == "__main__":
    test_pdf_generation()
