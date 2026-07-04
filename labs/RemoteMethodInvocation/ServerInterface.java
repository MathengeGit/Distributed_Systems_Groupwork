package labs.RemoteMethodInvocation;
import java.rmi.*;

public interface ServerInterface extends Remote{
    String concat(String a, String b) throws RemoteException;
    
}
