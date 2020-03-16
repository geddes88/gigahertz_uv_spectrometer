function GOMDBTS2048_setPassword(device: PChar): Integer; stdcall; external 'GOMDBTS2048.dll';
function GOMDBTS2048_getHandle(device: PChar; var handle: Integer): Integer; stdcall; external 'GOMDBTS2048.dll';
function GOMDBTS2048_releaseHandle(handle: Integer): Integer; stdcall; external 'GOMDBTS2048.dll';
 
procedure Main;
var 
    handle : Integer;
    returncode : Integer;
begin
    // unlock SDK
    returncode := GOMDBTS2048_setPassword(‘<password>’);
	// <password> must be replaced with real password
	
    // initialize BTS2048 device
    returncode := GOMDBTS2048_getHandle(‘BTS2048_0’, handle);
    // ... do something with handle ...
	
    // release resources
    returncode := GOMDBTS2048_releaseHandle(handle);
end;
