package labs.RemoteMethodInvocation;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;


public class Servant  extends UnicastRemoteObject implements ServerInterface {
    protected Servant() throws RemoteException {
        super();
    }
    @Override
    public String concat(String a, String b) throws RemoteException {
        return a + b;
    }

    
}
