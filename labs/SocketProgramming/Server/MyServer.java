package labs.SocketProgramming.Server;

import java.net.*;
import java.io.*;

public class MyServer {
    public static void main(String[] args) throws Exception {
        // Creating a port for communication 
        ServerSocket ss = new ServerSocket(5555);
        System.out.println("Server Initiated, Waiting for Client to Connect...");

        // Binding Client and Server on port 5555 
        Socket s = ss.accept();
        System.out.println("Client Connected");

        // Reading input from KeyBoard 
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        
        // Output and Input streams 
        OutputStream ostream = s.getOutputStream();
        PrintWriter pw = new PrintWriter(ostream, true);
        InputStream istream = s.getInputStream();
        BufferedReader receive = new BufferedReader(new InputStreamReader(istream));

        String clientMessage = "", serverMessage = "";
        while (true) {
            // Read client message 
            clientMessage = receive.readLine();
            System.out.println("Client: " + clientMessage);
            if (clientMessage.equals("bye")) break;

            // Server writing message 
            System.out.print("Server: ");
            serverMessage = br.readLine();
            pw.println(serverMessage);
            if (serverMessage.equals("bye")) break;
        }
        
        // Closing all connections 
        s.close();
        ss.close();
        istream.close();
        ostream.close();
        System.out.println("Connection Terminated");
    }
}
