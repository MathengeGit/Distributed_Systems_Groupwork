import java.io.*;
import java.net.*;

public class Client {
    public static void main(String[] args) throws Exception {
        String endpoint = "http://localhost:9999/ws/calculator";

        String soapRequest =
            "<?xml version=\"1.0\"?>" +
            "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ws=\"http://ws.learn.com/\">" +
            "<soapenv:Header/>" +
            "<soapenv:Body>" +
            "<ws:add><a>15</a><b>27</b></ws:add>" +
            "</soapenv:Body>" +
            "</soapenv:Envelope>";

        URL url = new URL(endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "text/xml; charset=utf-8");

        try (OutputStream os = conn.getOutputStream()) {
            os.write(soapRequest.getBytes("UTF-8"));
        }

        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String line, response = "";
        while ((line = br.readLine()) != null) response += line;
        br.close();

        System.out.println("SOAP Response:");
        System.out.println(response);
    }
}