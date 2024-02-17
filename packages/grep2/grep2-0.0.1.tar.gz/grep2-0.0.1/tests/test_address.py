import grep2

addresses = {
    'files/address/00.txt': "1357 Vine Street, Los Angeles, CA 90028",
    'files/address/01.txt': "123 Elm St, Springfield, IL 62704",
    'files/address/02.txt': "456 Pine St\nMetropolis, NV 89101",
    'files/address/03.txt': "800 Ocean View Blvd, Pacifica, CA 94044",
    'files/address/04.txt': "24 Maple Avenue,\nRiverdale, NY, 10471",
    'files/address/05.txt': "6789 College St, Boston, MA 02115",
    'files/address/06.txt': "The Grand Hotel\n789 Broadway Blvd\nNew York, NY 10003",
    'files/address/07.txt': "321 Cedar Ln, Knoxville, TN 37912",
    'files/address/08.txt': "5678 Park Place, Seattle, WA 98101",
    'files/address/09.txt': "ACME Corporation\n9876 Elm Street\nChicago, IL 60607",
}

def test_addresses():
    files = list(addresses.keys())
